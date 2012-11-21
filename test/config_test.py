from common import *
from logcatcolor.column import *
from logcatcolor.config import *
from logcatcolor.layout import *
from logcatcolor.profile import *
from logcatcolor.reader import *
import unittest

this_dir = os.path.abspath(os.path.dirname(__file__))
configs_dir = os.path.join(this_dir, "configs")

def config_test(config_file, wrap=None):
    def run_config_test(fn):
        def wrapped(self):
            path = os.path.join(configs_dir, config_file)
            fn(self, LogcatColorConfig(MockOptions(path, wrap)))
        return wrapped
    return run_config_test

class ConfigTest(unittest.TestCase):
    @config_test("")
    def test_default_config(self, config):
        self.assertEqual(config.get_default_layout(), config.DEFAULT_LAYOUT)
        self.assertEqual(config.get_column_width(MockColumn("tag", 20)), 20)
        self.assertEqual(config.get_wrap(), config.DEFAULT_WRAP)
        self.assertEqual(config.get_adb(), config.DEFAULT_ADB)

    @config_test("simple_config")
    def test_simple_config(self, config):
        self.assertEqual(config.get_default_layout(), "test")
        self.assertEqual(config.get_column_width(MockColumn("tag", 20)), 1)
        self.assertFalse(config.get_wrap())
        self.assertEqual(config.get_adb(), "/path/to/adb")

    @config_test("simple_config", wrap=True)
    def test_simple_config_override_wrap(self, config):
        self.assertTrue(config.get_wrap())
