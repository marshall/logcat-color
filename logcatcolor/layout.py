from colorama import Fore, Back, Style
from logcatcolor.column import *
import re
import StringIO

class Layout(object):
    MARKER_REGEX = re.compile(r"^--------- beginning of")
    MARKER_FORMAT = Fore.WHITE + Back.BLACK + Style.DIM + "%s" + Style.RESET_ALL
    def __init__(self, config, profile, width):
        self.columns = []
        self.config = config
        self.data = {}
        self.profile = profile
        self.width = width

        self.total_column_width = 0
        if self.COLUMNS:
            # first get the total column width, then construct each column
            for ColumnType in self.COLUMNS:
                self.total_column_width += config.get_column_width(ColumnType)

            for ColumnType in self.COLUMNS:
                column = ColumnType(self)
                self.columns.append(column)

        self.column_count = len(self.columns)

        if self.PATTERN:
            self.regex = re.compile(self.PATTERN)

    def match_marker(self, line):
        return self.MARKER_REGEX.match(line)

    def match_data(self, line):
        if not self.regex:
            return True

        match = self.regex.match(line)
        if not match:
            return False

        for name, value in match.groupdict().iteritems():
            self.data[name] = value.strip()
        return True

    def clear_data(self):
        self.data.clear()

    def include(self):
        if self.profile and not self.profile.include(self.data):
            return False

        return True

    def layout(self, line):
        if len(line) == 0:
            return None

        if self.match_marker(line):
            return self.layout_marker(line)

        if not self.match_data(line):
            return None

        if not self.include():
            self.clear_data()
            return None

        line = self.layout_columns(line)
        self.clear_data()
        return line

    def layout_marker(self, line):
        return self.MARKER_FORMAT % line

    def layout_columns(self, line):
        formatted = StringIO.StringIO()
        for index in range(0, self.column_count):
            column = self.columns[index]
            data = self.data[column.NAME]
            formatted.write(column.format(data))
            if index < self.column_count - 1:
                formatted.write(" ")

        return formatted.getvalue()

class RawLayout(Layout):
    NAME = "raw"
    def layout_columns(self, line):
       return line

class BriefLayout(Layout):
    "I/Tag(  PID): message"
    NAME = "brief"
    PRIORITY_PATTERN = r"(?P<priority>[A-Z])"
    PRIORITY_TAG_PATTERN = PRIORITY_PATTERN + r"/" + r"(?P<tag>.*?)"

    PID_PATTERN = r"(?P<pid>\d+)"
    PID_PAREN_PATTERN = r"\(\s*" + PID_PATTERN + r"\)"
    MESSAGE_PATTERN = r"(?P<message>.*?)"

    BRIEF_PATTERN = PRIORITY_TAG_PATTERN + \
              PID_PAREN_PATTERN + r": " + \
              MESSAGE_PATTERN
    PATTERN = r"^" + BRIEF_PATTERN + r"$"
    COLUMNS = (PIDColumn, TagColumn, PriorityColumn, MessageColumn)

class ProcessLayout(Layout):
    "I(  PID) message (Tag)"
    NAME = "process"
    PATTERN = r"^" + BriefLayout.PRIORITY_PATTERN + \
             BriefLayout.PID_PAREN_PATTERN + r" " + \
             BriefLayout.MESSAGE_PATTERN + r" " + \
             r"\((?P<tag>.+)\)$"
    COLUMNS = BriefLayout.COLUMNS

class TagLayout(Layout):
    "I/Tag  : message"
    NAME = "tag"
    PATTERN = r"^" + BriefLayout.PRIORITY_TAG_PATTERN + r": " + \
              BriefLayout.MESSAGE_PATTERN + r"$"
    COLUMNS = (TagColumn, PriorityColumn, MessageColumn)

class ThreadLayout(Layout):
    "I(  PID:TID) message"
    NAME = "thread"
    TID_HEX_PATTERN = r"(?P<tid>0x[0-9a-f]+)"
    PID_TID_HEX_PATTERN = BriefLayout.PID_PATTERN + r":" + TID_HEX_PATTERN

    PATTERN = r"^" + BriefLayout.PRIORITY_PATTERN + \
              r"\(\s*" + PID_TID_HEX_PATTERN + r"\) " + \
              BriefLayout.MESSAGE_PATTERN + r"$"
    COLUMNS = (PIDColumn, TIDColumn, PriorityColumn, MessageColumn)

class TimeLayout(Layout):
    "MM-DD HH:MM:SS.mmm D/Tag(  PID): message"
    NAME = "time"
    DATE_TIME_PATTERN = r"(?P<date>\d\d-\d\d)\s(?P<time>\d\d:\d\d:\d\d\.\d\d\d)"
    PATTERN = r"^" + DATE_TIME_PATTERN + r" " + BriefLayout.BRIEF_PATTERN + r"$"
    COLUMNS = (DateColumn, TimeColumn, ) + BriefLayout.COLUMNS

class ThreadTimeLayout(Layout):
    "MM-DD HH:MM:SS.mmm   PID   TID I ONCRPC  : rpc_handle_rpc_call: Find Status: 0 Xid: 7062"
    NAME = "threadtime"
    PATTERN = r"^" + TimeLayout.DATE_TIME_PATTERN + r"\s+" + \
              BriefLayout.PID_PATTERN + r"\s+" + \
              r"(?P<tid>\d+)\s+" + \
              BriefLayout.PRIORITY_PATTERN + r"\s+" + \
              r"(?P<tag>.*?)\s*: " + \
              BriefLayout.MESSAGE_PATTERN + r"$"
    COLUMNS = (DateColumn, TimeColumn, PIDColumn, TIDColumn, TagColumn, PriorityColumn, MessageColumn)

class LongLayout(Layout):
    "[ MM-DD HH:MM:SS.mmm   PID:TID I/Tag ]\nmessage"
    NAME = "long"
    PATTERN = r"^\[ " + TimeLayout.DATE_TIME_PATTERN + r"\s+" + \
                   ThreadLayout.PID_TID_HEX_PATTERN + r"\s+" + \
                   BriefLayout.PRIORITY_TAG_PATTERN + r"\s+\]$"
    COLUMNS = ThreadTimeLayout.COLUMNS

    def match_data(self, line):
        if not Layout.match_data(self, line):
            self.data["message"] = line

        return "message" in self.data and "tag" in self.data
