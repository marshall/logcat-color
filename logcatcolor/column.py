"""
logcat-color

Copyright 2012, Marshall Culpepper
Licensed under the Apache License, Version 2.0

Columns for displaying logcat log data
"""
import colorama
from colorama import Fore, Back, Style
import StringIO

colorama.init()

class Column(object):
    def __init__(self, layout):
        self.width = layout.config.get_column_width(self)

    def format(self, data):
        return self.FORMAT % data

class DateColumn(Column):
    NAME = "date"
    FORMAT = Fore.WHITE + Back.BLACK + Style.DIM + \
             "%s" + Style.RESET_ALL
    DEFAULT_WIDTH = 7

class TimeColumn(Column):
    NAME = "time"
    FORMAT = Fore.WHITE + Back.BLACK + Style.DIM + \
             "%s" + Style.RESET_ALL
    DEFAULT_WIDTH = 14

class PIDColumn(Column):
    NAME = "pid"
    DEFAULT_WIDTH = 8
    FORMAT = Fore.WHITE + Back.BLACK + Style.DIM + \
             "%s" + Style.RESET_ALL

    def format(self, pid):
        # center process info
        if self.width > 0:
            pid = pid.center(self.width)

        return Column.format(self, pid)

class TIDColumn(PIDColumn):
    NAME = "tid"

    def format(self, tid):
        # normalize thread IDs to be decimal
        if "0x" in tid:
            tid = str(int(tid, 16))

        return PIDColumn.format(self, tid)

class TagColumn(Column):
    NAME = "tag"
    DEFAULT_WIDTH = 20
    COLOR_NAMES = ("RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE")
    COLOR_MAP = {}

    @classmethod
    def init_color_map(cls):
        for color in cls.COLOR_NAMES:
            cls.COLOR_MAP[color] = getattr(Fore, color)

    def __init__(self, layout):
        Column.__init__(self, layout)

        tag_colors = None
        if layout.profile:
            tag_colors = layout.profile.tag_colors

        self.tag_colors = tag_colors or {}
        self.last_used = self.COLOR_MAP.values()[:]

    # This will allocate a unique format for the given tag since we dont have
    # very many colors, we always keep track of the LRU
    def allocate_color(self, tag):
        if tag not in self.tag_colors:
            self.tag_colors[tag] = self.last_used[0]

        color = self.tag_colors[tag]
        self.last_used.remove(color)
        self.last_used.append(color)
        return color

    def format(self, tag):
        color = self.allocate_color(tag)
        if self.width > 2:
            if self.width < len(tag):
                tag = tag[0:self.width-2] + ".."

        tag = tag.rjust(self.width)
        return color + Style.DIM + tag + Style.RESET_ALL

TagColumn.init_color_map()

class PriorityColumn(Column):
    NAME = "priority"
    DEFAULT_WIDTH = 3
    COLORS = {
        "V": Fore.WHITE + Back.BLACK,
        "D": Fore.BLACK + Back.BLUE,
        "I": Fore.BLACK + Back.GREEN,
        "W": Fore.BLACK + Back.YELLOW,
        "E": Fore.BLACK + Back.RED,
        "F": Fore.BLACK + Back.RED
    }

    def __init__(self, layout):
        Column.__init__(self, layout)
        self.formats = {}
        for priority in self.COLORS.keys():
            self.formats[priority] = self.COLORS[priority] + \
                priority.center(self.width) + Style.RESET_ALL

    def format(self, priority):
        return self.formats[priority]

class MessageColumn(Column):
    NAME = "message"
    DEFAULT_WIDTH = 0
    def __init__(self, layout):
        self.width = None
        self.left = layout.total_column_width
        if layout.config.get_wrap() and (not layout.profile or layout.profile.wrap):
            self.width = layout.width - self.left

    def format(self, message):
        # Don't wrap when width is None
        if not self.width:
            return message

        messagebuf = StringIO.StringIO()
        current = 0
        while current < len(message):
            next = min(current + self.width, len(message))
            messagebuf.write(message[current:next])
            if next < len(message):
                messagebuf.write("\n%s" % (" " * self.left))
            current = next
        return messagebuf.getvalue()
