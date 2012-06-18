import colorama
from colorama import Fore, Back, Style
import StringIO

colorama.init()

class PIDColumn(object):
    FORMAT = Fore.WHITE + Back.BLACK + Style.DIM + \
             "%s" + Style.RESET_ALL
    def __init__(self, width):
        self.width = width

    def format(self, pid):
        # center process info
        if self.width > 0:
            pid = pid.center(self.width)

        return self.FORMAT % pid

class TagColumn(object):
    COLOR_NAMES = ("RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE")
    COLOR_MAP = {}

    @classmethod
    def init_color_map(cls):
        for color in cls.COLOR_NAMES:
            cls.COLOR_MAP[color] = getattr(Fore, color)

    def __init__(self, width, tag_colors=None):
        self.width = width
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

class PriorityColumn(object):
    COLORS = {
        "V": Fore.WHITE + Back.BLACK,
        "D": Fore.BLACK + Back.BLUE,
        "I": Fore.BLACK + Back.GREEN,
        "W": Fore.BLACK + Back.YELLOW,
        "E": Fore.BLACK + Back.RED
    }

    def __init__(self, width):
        self.formats = {}
        for priority in ("V", "D", "I", "W", "E"):
            self.formats[priority] = self.COLORS[priority] + \
                priority.center(width) + Style.RESET_ALL

    def format(self, priority):
        return self.formats[priority]

class MessageColumn(object):
    def __init__(self, left, width):
        self.left = left
        self.width = width

    def format(self, message):
        messagebuf = StringIO.StringIO()
        current = 0
        while current < len(message):
            next = min(current + self.width, len(message))
            messagebuf.write(message[current:next])
            if next < len(message):
                messagebuf.write("\n%s" % (" " * self.left))
            current = next
        return messagebuf.getvalue()
