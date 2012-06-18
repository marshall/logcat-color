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

    def layout(self, line):
        match = self.REGEX.match(line)
        if not match:
            return None

        formatted = StringIO.StringIO()
        priority, tag, pid, message = match.groups()
        pid = pid.strip()
        priority = priority.strip()
        tag = tag.strip()
        message = message.strip()

        if self.profile and not self.profile.include(tag, priority, message):
            return None

        column_data = (pid, tag, priority, message)

        for index in range(0, self.column_count):
            data = column_data[index]
            column = self.columns[index]
            formatted.write(column.format(data))
            if index < self.column_count - 1:
                formatted.write(" ")

        return formatted.getvalue()
