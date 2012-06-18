from logcatcolor.column import TagColumn
from logcatcolor.profile import Profile
import os
import platform
import re
import sys
import traceback

class LogcatColorConfig(object):
    DEFAULT_LAYOUT = "brief"
    DEFAULT_PID_WIDTH = 8
    DEFAULT_TAG_WIDTH = 20
    DEFAULT_PRIORITY_WIDTH = 3

    def __init__(self, path=None):
        self.path = path or self.get_default_config()
        self.filters = {}

        builtins = { "Profile": Profile }
        builtins.update(TagColumn.COLOR_MAP)
        self.config = {"__builtins__": builtins}

        if os.path.exists(self.path):
            # config file is just a python script that globals are imported from
            try:
                execfile(self.path, self.config)
            except:
                self.report_config_error()
                sys.exit(1)

            # execfile puts builtins into our "global", so clean them out
            del self.config["__builtins__"]

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

    def get_default_layout(self):
        return self.config.get("default_layout", self.DEFAULT_LAYOUT)

    def get_pid_width(self):
        return self.config.get("pid_width", self.DEFAULT_PID_WIDTH)

    def get_tag_width(self):
        return self.config.get("tag_width", self.DEFAULT_TAG_WIDTH)

    def get_priority_width(self):
        return self.config.get("priority_width", self.DEFAULT_PRIORITY_WIDTH)
