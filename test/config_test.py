from common import *
from logcatcolor.column import *
from logcatcolor.config import *
from logcatcolor.layout import *
from logcatcolor.profile import *
from logcatcolor.reader import *
import unittest

this_dir = os.path.abspath(os.path.dirname(__file__))
configs_dir = os.path.join(this_dir, "configs")

def config_test(config_file, wrap=None, stay_connected=None):
    def run_config_test(fn):
        def wrapped(self):
            path = os.path.join(configs_dir, config_file)
            options = MockObject(config=path,
                                 wrap=wrap,
                                 stay_connected=stay_connected)
            fn(self, LogcatColorConfig(options))
        return wrapped
    return run_config_test

class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tag_column = MockObject(NAME="tag", DEFAULT_WIDTH=20)

    @config_test("")
    def test_default_config(self, config):
        self.assertEqual(config.get_default_layout(), config.DEFAULT_LAYOUT)
        self.assertEqual(config.get_column_width(self.tag_column), 20)
        self.assertEqual(config.get_wrap(), config.DEFAULT_WRAP)
        self.assertEqual(config.get_adb(), config.DEFAULT_ADB)
        self.assertEqual(config.get_stay_connected(), config.DEFAULT_STAY_CONNECTED)

    @config_test("simple_config")
    def test_simple_config(self, config):
        self.assertEqual(config.get_default_layout(), "test")
        self.assertEqual(config.get_column_width(self.tag_column), 1)
        self.assertFalse(config.get_wrap())
        self.assertEqual(config.get_adb(), "/path/to/adb")
        self.assertEqual(config.get_stay_connected(), True)

    @config_test("simple_config", wrap=True, stay_connected=True)
    def test_simple_config_overrides(self, config):
        self.assertTrue(config.get_wrap())
        self.assertTrue(config.get_stay_connected())
