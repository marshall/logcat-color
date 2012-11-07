import unittest
from logcatcolor.column import *
from logcatcolor.config import *
from logcatcolor.layout import *
from logcatcolor.profile import *
from logcatcolor.reader import *

MARKER_LINE = "--------- beginning of /dev/log/main"
BRIEF_LINE  = "I/Tag(  123): message"
PROCESS_LINE = "I(  123) message (Tag)"
TAG_LINE = "I/Tag  : message"
THREAD_LINE = "I(  123:0x123) message"
TIME_LINE = "01-02 12:34:56.000 D/Tag(  123): message"
THREAD_TIME_LINE = "01-02 12:34:56.000   123   456 I Tag  : message"
LONG_LINES = ["[ 01-02 12:34:56.000   123:0x123 I/Tag ]", "message"]

def layout_test(LayoutType):
    def run_layout_test(fn):
        def wrapped(self):
            options = lambda: None
            options.config = ""
            options.wrap = False
            config = LogcatColorConfig(options)
            layout = LayoutType(config, None, 2000)
            fn(self, layout)
        return wrapped
    return run_layout_test

class LayoutTest(unittest.TestCase):
    @layout_test(BriefLayout)
    def test_marker(self, layout):
        self.assertTrue(layout.match_marker(MARKER_LINE))

    @layout_test(RawLayout)
    def test_raw_layout(self, layout):
        self.assertEqual(BRIEF_LINE, layout.layout(BRIEF_LINE))

    @layout_test(BriefLayout)
    def test_brief_layout(self, layout):
        self.assertFalse(layout.match_marker(BRIEF_LINE))
        self.assertTrue(layout.match_data(BRIEF_LINE))
        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["message"], "message")

    @layout_test(ProcessLayout)
    def test_process_layout(self, layout):
        self.assertTrue(layout.match_data(PROCESS_LINE))
        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["message"], "message")

    @layout_test(TagLayout)
    def test_tag_layout(self, layout):
        self.assertTrue(layout.match_data(TAG_LINE))
        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["message"], "message")

    @layout_test(ThreadLayout)
    def test_thread_layout(self, layout):
        self.assertTrue(layout.match_data(THREAD_LINE))
        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["tid"], "0x123")

    @layout_test(TimeLayout)
    def test_time_layout(self, layout):
        self.assertTrue(layout.match_data(TIME_LINE))
        self.assertEqual(layout.data["priority"], "D")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["message"], "message")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["date"], "01-02")
        self.assertEqual(layout.data["time"], "12:34:56.000")

    @layout_test(ThreadTimeLayout)
    def test_thread_time_layout(self, layout):
        self.assertTrue(layout.match_data(THREAD_TIME_LINE))
        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["tid"], "456")
        self.assertEqual(layout.data["message"], "message")
        self.assertEqual(layout.data["date"], "01-02")
        self.assertEqual(layout.data["time"], "12:34:56.000")

    @layout_test(LongLayout)
    def test_long_layout(self, layout):
        self.assertFalse(layout.match_data(LONG_LINES[0]))
        self.assertTrue(layout.match_data(LONG_LINES[1]))

        self.assertEqual(layout.data["priority"], "I")
        self.assertEqual(layout.data["tag"], "Tag")
        self.assertEqual(layout.data["pid"], "123")
        self.assertEqual(layout.data["tid"], "0x123")
        self.assertEqual(layout.data["date"], "01-02")
        self.assertEqual(layout.data["time"], "12:34:56.000")
