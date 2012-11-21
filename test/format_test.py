from common import *
from logcatcolor.format import *
import unittest

MARKER_LINE = "--------- beginning of /dev/log/main"
BRIEF_LINE  = "I/Tag(  123): message"
PROCESS_LINE = "I(  123) message (Tag)"
TAG_LINE = "I/Tag  : message"
THREAD_LINE = "I(  123:0x123) message"
TIME_LINE = "01-02 12:34:56.000 D/Tag(  123): message"
THREAD_TIME_LINE = "01-02 12:34:56.000   123   456 I Tag  : message"
LONG_LINES = ["[ 01-02 12:34:56.000   123:0x123 I/Tag ]", "message"]

def format_test(FormatType):
    def run_format_test(fn):
        def wrapped(self):
            fn(self, FormatType())
        return wrapped
    return run_format_test

class FormatTest(unittest.TestCase):
    @format_test(BriefFormat)
    def test_marker(self, format):
        self.assertNotEqual(Format.MARKER_REGEX.match(MARKER_LINE), None)

    @format_test(BriefFormat)
    def test_brief_format(self, format):
        self.assertTrue(format.match(BRIEF_LINE))
        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("tid"), None)
        self.assertEqual(format.get("date"), None)
        self.assertEqual(format.get("time"), None)

    @format_test(ProcessFormat)
    def test_process_format(self, format):
        self.assertTrue(format.match(PROCESS_LINE))
        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("tid"), None)
        self.assertEqual(format.get("date"), None)
        self.assertEqual(format.get("time"), None)

    @format_test(TagFormat)
    def test_tag_format(self, format):
        self.assertTrue(format.match(TAG_LINE))
        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("pid"), None)
        self.assertEqual(format.get("tid"), None)
        self.assertEqual(format.get("date"), None)
        self.assertEqual(format.get("time"), None)

    @format_test(ThreadFormat)
    def test_thread_format(self, format):
        self.assertTrue(format.match(THREAD_LINE))
        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("tid"), "0x123")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("tag"), None)
        self.assertEqual(format.get("date"), None)
        self.assertEqual(format.get("time"), None)

    @format_test(TimeFormat)
    def test_time_format(self, format):
        self.assertTrue(format.match(TIME_LINE))
        self.assertEqual(format.get("priority"), "D")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("date"), "01-02")
        self.assertEqual(format.get("time"), "12:34:56.000")
        self.assertEqual(format.get("tid"), None)

    @format_test(ThreadTimeFormat)
    def test_thread_time_format(self, format):
        self.assertTrue(format.match(THREAD_TIME_LINE))
        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("tid"), "456")
        self.assertEqual(format.get("message"), "message")
        self.assertEqual(format.get("date"), "01-02")
        self.assertEqual(format.get("time"), "12:34:56.000")

    @format_test(LongFormat)
    def test_long_format(self, format):
        self.assertFalse(format.match(LONG_LINES[0]))
        self.assertTrue(format.match(LONG_LINES[1]))

        self.assertEqual(format.get("priority"), "I")
        self.assertEqual(format.get("tag"), "Tag")
        self.assertEqual(format.get("pid"), "123")
        self.assertEqual(format.get("tid"), "0x123")
        self.assertEqual(format.get("date"), "01-02")
        self.assertEqual(format.get("time"), "12:34:56.000")
        self.assertEqual(format.get("message"), "message")

    def test_detect_format(self):
        self.assertEqual(detect_format([MARKER_LINE, BRIEF_LINE]), "brief")
        self.assertEqual(detect_format([MARKER_LINE, PROCESS_LINE]), "process")
        self.assertEqual(detect_format([MARKER_LINE, TAG_LINE]), "tag")
        self.assertEqual(detect_format([MARKER_LINE, THREAD_LINE]), "thread")
        self.assertEqual(detect_format([MARKER_LINE, TIME_LINE]), "time")
        self.assertEqual(detect_format([MARKER_LINE, THREAD_TIME_LINE]), "threadtime")
        self.assertEqual(detect_format([MARKER_LINE, LONG_LINES[0], LONG_LINES[1]]), "long")
        self.assertEqual(detect_format([MARKER_LINE]), None)
