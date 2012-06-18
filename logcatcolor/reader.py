import asyncore
import asynchat
import fcntl
from logcatcolor.layout import *
import os

# Parts copied from asyncore.file_dispatcher
class FileLineReader(asynchat.async_chat):
    LINE_TERMINATOR = "\n"

    def __init__(self, fd):
        asynchat.async_chat.__init__(self)
        self.connected = True
        self.log_buffer = []

        self.set_file(fd)
        self.set_terminator(self.LINE_TERMINATOR)

    def set_file(self, fd):
        try:
            # fd may be a file object
            fd = fd.fileno()
        except AttributeError:
            pass

        self.socket = asyncore.file_wrapper(fd)
        self._fileno = self.socket.fileno()
        self.add_channel()

        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def collect_incoming_data(self, data):
        self.log_buffer.append(data)

    def found_terminator(self):
        line = "".join(self.log_buffer)
        self.process_line(line)
        self.log_buffer = []

    def process_line(self):
        pass

class LogcatReader(FileLineReader):
    # TODO support other logcat logging formats:
    # process, tag, raw, time, threadtime, long
    layouts = {
        "brief": BriefLayout
    }

    def __init__(self, file, config, profile=None, layout="brief", width=80):
        FileLineReader.__init__(self, file)
        layoutType = self.layouts[layout]
        self.layout = layoutType(config, profile, width)

    def process_line(self, line):
        formatted = self.layout.layout(line)
        if formatted:
            print formatted
