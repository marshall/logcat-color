"""
logcat-color

Copyright 2012, Marshall Culpepper
Licensed under the Apache License, Version 2.0

Support for reading various logcat logging formats into an easier to consume
data map.
"""
import re

def format(cls):
    Format.TYPES[cls.NAME] = cls
    Format.REGEXES[cls.NAME] = re.compile(cls.PATTERN) if cls.PATTERN else None
    return cls

class Format(object):
    TYPES = {}
    REGEXES = {}
    MARKER_REGEX = re.compile(r"^--------- beginning of")

    def __init__(self):
        self.data = {}
        self.regex = self.REGEXES[self.NAME]

    def match(self, line):
        if not self.regex:
            return True

        self.data["line"] = line
        match = self.regex.match(line)
        if not match:
            return False

        for name, value in match.groupdict().iteritems():
            self.data[name] = value.strip()
        return True

    def get(self, name):
        return self.data.get(name)

    def include(self, profile):
        if profile and not profile.include(self.data):
            return False
        return True

@format
class BriefFormat(Format):
    "I/Tag(  PID): message"
    NAME = "brief"
    PRIORITY_PATTERN = r"(?P<priority>[A-Z])"
    PRIORITY_TAG_PATTERN = PRIORITY_PATTERN + r"/" + r"(?P<tag>[^\(]*?)"

    PID_PATTERN = r"(?P<pid>\d+)"
    PID_PAREN_PATTERN = r"\(\s*" + PID_PATTERN + r"\)"
    MESSAGE_PATTERN = r"(?P<message>.*?)"

    BRIEF_PATTERN = PRIORITY_TAG_PATTERN + \
              PID_PAREN_PATTERN + r": " + \
              MESSAGE_PATTERN
    PATTERN = r"^" + BRIEF_PATTERN + r"$"

@format
class ProcessFormat(Format):
    "I(  PID) message (Tag)"
    NAME = "process"
    PATTERN = r"^" + BriefFormat.PRIORITY_PATTERN + \
             BriefFormat.PID_PAREN_PATTERN + r" " + \
             BriefFormat.MESSAGE_PATTERN + r" " + \
             r"\((?P<tag>.+)\)$"

@format
class TagFormat(Format):
    "I/Tag  : message"
    NAME = "tag"
    PATTERN = r"^" + BriefFormat.PRIORITY_TAG_PATTERN + r": " + \
              BriefFormat.MESSAGE_PATTERN + r"$"

@format
class ThreadFormat(Format):
    "I(  PID:TID) message"
    NAME = "thread"
    TID_HEX_PATTERN = r"(?P<tid>0x[0-9a-f]+)"
    PID_TID_HEX_PATTERN = BriefFormat.PID_PATTERN + r":" + TID_HEX_PATTERN

    PATTERN = r"^" + BriefFormat.PRIORITY_PATTERN + \
              r"\(\s*" + PID_TID_HEX_PATTERN + r"\) " + \
              BriefFormat.MESSAGE_PATTERN + r"$"

@format
class TimeFormat(Format):
    "MM-DD HH:MM:SS.mmm D/Tag(  PID): message"
    NAME = "time"
    DATE_TIME_PATTERN = r"(?P<date>\d\d-\d\d)\s(?P<time>\d\d:\d\d:\d\d\.\d\d\d)"
    PATTERN = r"^" + DATE_TIME_PATTERN + r" " + BriefFormat.BRIEF_PATTERN + r"$"

@format
class ThreadTimeFormat(Format):
    "MM-DD HH:MM:SS.mmm   PID   TID I ONCRPC  : rpc_handle_rpc_call: Find Status: 0 Xid: 7062"
    NAME = "threadtime"
    PATTERN = r"^" + TimeFormat.DATE_TIME_PATTERN + r"\s+" + \
              BriefFormat.PID_PATTERN + r"\s+" + \
              r"(?P<tid>\d+)\s+" + \
              BriefFormat.PRIORITY_PATTERN + r"\s+" + \
              r"(?P<tag>.*?)\s*: " + \
              BriefFormat.MESSAGE_PATTERN + r"$"

@format
class LongFormat(Format):
    "[ MM-DD HH:MM:SS.mmm   PID:TID I/Tag ]\nmessage"
    NAME = "long"
    PATTERN = r"^\[ " + TimeFormat.DATE_TIME_PATTERN + r"\s+" + \
                   ThreadFormat.PID_TID_HEX_PATTERN + r"\s+" + \
                   BriefFormat.PRIORITY_TAG_PATTERN + r"\s+\]$"

    def match(self, line):
        if not Format.match(self, line):
            self.data["message"] = line

        return "message" in self.data and "tag" in self.data

"""
A helper to detect the log format from a list of lines
"""
def detect_format(lines):
    if len(lines) == 0:
        return None

    for line in lines:
        if Format.MARKER_REGEX.match(line):
            continue

        for name, regex in Format.REGEXES.iteritems():
            if regex.match(line):
                return name

    return None
