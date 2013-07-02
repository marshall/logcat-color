import common
import json
import os
from StringIO import StringIO
from subprocess import Popen, PIPE
import sys
import tempfile
import unittest

from common import LogcatColor, MockAdbLogcatColor
this_dir = os.path.dirname(os.path.abspath(__file__))

def logcat_color_test(*args, **kwargs):
    def run_logcat_color_test(fn):
        def wrapped(self):
            self.start_logcat_color(*args, **kwargs)
            fn(self)
        return wrapped
    return run_logcat_color_test

logs_dir = os.path.join(this_dir, "logs")
configs_dir = os.path.join(this_dir, "configs")

BRIEF_LOG = os.path.join(logs_dir, "brief_log")
BRIEF_FILTER_CONFIG = os.path.join(configs_dir, "brief_filter_config")
EMPTY_CONFIG = os.path.join(configs_dir, "empty_config")

tmpfd, tmpout = tempfile.mkstemp()
os.close(tmpfd)

class LogcatColorTest(unittest.TestCase):
    DEBUG = False

    def setUp(self):
        # Clear out our temporary output file before each test
        global tmpout
        with open(tmpout, "w") as f: f.write("")

    def start_logcat_color(self, *args, **kwargs):
        args = list(args)
        args.insert(0, common.logcat_color)
        if "config" in kwargs:
            args[1:1] = ["--config", kwargs["config"]]
            del kwargs["config"]
        elif "--config" not in args:
            # fall back to empty config
            args[1:1] = ["--config", EMPTY_CONFIG]

        piped = ""
        piped_path = None
        if "piped" in kwargs:
            piped_path = kwargs["piped"]
            piped = open(piped_path, "r").read()
            del kwargs["piped"]
        elif "input" in kwargs:
            piped = None
            args[1:1] = ["--input", kwargs["input"]]
            del kwargs["input"]

        if self.DEBUG:
            piped_debug = ""
            if piped_path:
                piped_debug = " < %s" % piped_path

            print " ".join(args) + piped_debug

        self.proc = Popen(args, stdout=PIPE, stderr=PIPE, stdin=PIPE, **kwargs)
        self.out, self.err = self.proc.communicate(piped)

        self.filter_results = common.read_filter_results()
        if os.path.exists(common.filter_results):
            os.unlink(common.filter_results)

        if self.DEBUG and self.err:
            print >>sys.stderr, self.err

    @logcat_color_test(piped=BRIEF_LOG)
    def test_piped_input(self):
        self.assertEqual(self.proc.returncode, 0)

    @logcat_color_test(config="/does/not/exist")
    def test_invalid_config(self):
        self.assertNotEqual(self.proc.returncode, 0)

    @logcat_color_test("--plain", input=BRIEF_LOG)
    def test_plain_logging(self):
        self.assertEqual(self.proc.returncode, 0)
        brief_data = open(BRIEF_LOG, "r").read()
        self.assertEqual(self.out, brief_data)

    @logcat_color_test("--plain", "brief_filter_fn",
        input=BRIEF_LOG, config=BRIEF_FILTER_CONFIG)
    def test_plain_logging_with_fn_filter(self):
        self.assertEqual(self.proc.returncode, 0)
        self.assertTrue("(  123)" not in self.out)
        self.assertTrue("( 890)" not in self.out)
        self.assertTrue("( 234)" in self.out)
        self.assertTrue("( 567)" in self.out)

        filter_results = self.filter_results.get("brief_filter_fn")
        self.assertNotEqual(filter_results, None)
        self.assertEqual(len(filter_results), 4)

        for result in filter_results:
            self.assertTrue("result" in result)
            self.assertTrue("data" in result)

        def assertResult(result, value, priority, tag, pid, msg):
            self.assertTrue("result" in result)
            self.assertEqual(result["result"], value)

            data = result["data"]
            self.assertEqual(data["priority"], priority)
            self.assertEqual(data["tag"], tag)
            self.assertEqual(data["pid"], pid)
            self.assertEqual(data["message"], msg)

        assertResult(filter_results[0], False, "I", "Tag", "123", "message")
        assertResult(filter_results[1], True, "I", "Tag2", "234", "message 2")
        assertResult(filter_results[2], True, "I", "Tag3", "567", "message 3")
        assertResult(filter_results[3], False, "I", "Tag4", "890", "message 4")

    @logcat_color_test("--plain", "brief_filter_tag",
        input=BRIEF_LOG, config=BRIEF_FILTER_CONFIG)
    def test_plain_logging_with_tag_filter(self):
        self.assertEqual(self.proc.returncode, 0)
        self.assertTrue("Tag1" not in self.out)
        self.assertTrue("Tag3" not in self.out)
        self.assertTrue("Tag2" in self.out)
        self.assertTrue("Tag4" in self.out)

    @logcat_color_test("--plain", "--output", tmpout, input=BRIEF_LOG)
    def test_file_output(self):
        self.assertEqual(self.proc.returncode, 0)
        brief_data = open(BRIEF_LOG, "r").read()
        out_data = open(tmpout, "r").read()
        self.assertEqual(out_data, brief_data)

    def test_logcat_options_with_filters(self):
        # Make sure logcat flags come before filter arguments
        # https://github.com/marshall/logcat-color/issues/5
        lc = LogcatColor(args=["-v", "time", "Tag1:V", "*:S", "--silent",
                               "--print-size", "--dump", "--clear"])
        self.assertEqual(lc.format, "time")

        args = lc.get_logcat_args()

        self.assertEqual(len(args), 8)

        format_index = args.index("-v")
        self.assertTrue(format_index >= 0)
        self.assertEqual(args[format_index+1], "time")
        self.assertTrue("-s" in args)
        self.assertTrue("-d" in args)
        self.assertTrue("-g" in args)
        self.assertTrue("-c" in args)

        self.assertEqual(args[-2], "Tag1:V")
        self.assertEqual(args[-1], "*:S")

    def test_stay_connected(self):
        lc = MockAdbLogcatColor(BRIEF_LOG, tmpout,
                                args=["-s", "serial123", "--stay-connected",
                                      "--config", EMPTY_CONFIG],
                                max_wait_count=3)
        self.assertEqual(lc.config.get_stay_connected(), True)

        lc.loop()
        self.assertEqual(lc.wait_count, 3)

        results = json.loads(open(tmpout, "r").read())
        self.assertEqual(len(results), 6)

        logcat_results = filter(lambda d: d["command"] == "logcat", results)
        self.assertEqual(len(logcat_results), 3)

        wait_results = filter(lambda d: d["command"] == "wait-for-device", results)
        self.assertEquals(len(wait_results), 3)

        for r in results:
            self.assertEqual(r["serial"], "serial123")

