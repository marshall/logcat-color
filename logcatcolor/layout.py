from logcatcolor.column import *
import re
import StringIO

class BriefLayout(object):
    "I/Tag(  PID): message"
    REGEX = re.compile("^([A-Z])/([^\(]+)\(([^\)]+)\): (.*)$")

    def __init__(self, config, profile, width):
        message_left = config.get_pid_width() + \
            config.get_tag_width() + \
            config.get_priority_width() + 3

        self.profile = None
        if profile:
            self.profile = profile

        tag_colors = None
        if profile:
            tag_colors = profile.get_tag_colors()

        self.columns = (
            PIDColumn(config.get_pid_width()),
            TagColumn(config.get_tag_width(), tag_colors=tag_colors),
            PriorityColumn(config.get_priority_width()),
            MessageColumn(message_left, width - message_left)
        )
        self.column_count = len(self.columns)

    def init_log_data(self, line):
        match = self.REGEX.match(line)
        if not match:
            return False

        self.priority, self.tag, self.pid, self.message = \
            (m.strip() for m in match.groups())
        return True

    def clean_log_data(self):
        self.priority = self.tag = self.pid = self.message = None

    def include(self):
        if self.profile and not self.profile.include(
            self.tag, self.priority, self.message):
            return False

        return True

    def layout(self, line):
        if not self.init_log_data(line):
            return None

        if not self.include():
            self.clean_log_data()
            return None

        column_data = (self.pid, self.tag, self.priority, self.message)
        formatted = StringIO.StringIO()

        for index in range(0, self.column_count):
            data = column_data[index]
            column = self.columns[index]
            formatted.write(column.format(data))
            if index < self.column_count - 1:
                formatted.write(" ")

        self.clean_log_data()
        return formatted.getvalue()

class PlainLayout(BriefLayout):

    def layout(self, line):
        if not self.init_log_data(line):
            return None

        if not self.include():
            self.clean_log_data()
            return None

        self.clean_log_data()
        return line
