from logcatcolor.column import TagColumn
from logcatcolor.profile import Profile
import os
import platform
import re
import sys
import traceback

class LogcatColorConfig(object):
    DEFAULT_LAYOUT = "brief"
    DEFAULT_WRAP = True
    DEFAULT_ADB = None

    def __init__(self, options):
        self.options = options
        self.path = options.config or self.get_default_config()
        self.filters = {}

        self.config = { "Profile":  Profile }
        self.config.update(TagColumn.COLOR_MAP)

        if os.path.exists(self.path):
            # config file is just a python script that globals are imported from
            try:
                execfile(self.path, self.config)
            except:
                self.report_config_error()
                sys.exit(1)

            # clean up builtins and globals from self.config
            del self.config["__builtins__"]
            del self.config["Profile"]
            for color in TagColumn.COLOR_MAP.keys():
                del self.config[color]

        self.load_config()

    def report_config_error(self):
        config_error = """
########################################
# There was an error loading config from
# %(path)s
########################################

%(error)s"""

        print >>sys.stderr, config_error % {
            "path": self.path,
            "error": traceback.format_exc()
        }

    def get_default_config(self):
        env_key = "HOME"
        if platform.system() == "Windows":
            env_key = "USERPROFILE"

        home_dir = os.environ[env_key]
        return os.path.join(home_dir, ".logcat-color")

    def load_config(self):
        if self.options.wrap is None:
            self.wrap = True
            if "wrap" in self.config:
                self.wrap = self.config["wrap"]

    def get_default_layout(self):
        return self.config.get("default_layout", self.DEFAULT_LAYOUT)

    def get_column_width(self, column):
        return self.config.get(column.NAME + "_width", column.DEFAULT_WIDTH)

    def get_wrap(self):
        return self.config.get("wrap", self.DEFAULT_WRAP)

    def get_adb(self):
        return self.config.get("adb", self.DEFAULT_ADB)
