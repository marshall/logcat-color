import asyncore
import asynchat
import fcntl
import inspect
import logcatcolor.layout
import os
import sys
import traceback

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
        try:
            self.process_line(line)
        except:
            traceback.print_exc()
            sys.exit(1)

        self.log_buffer = []

    def process_line(self):
        pass

class LogcatReader(FileLineReader):
    LAYOUTS = {}
    def __init__(self, file, config, profile=None, layout="brief", width=80):
        FileLineReader.__init__(self, file)
        LayoutType = self.LAYOUTS[layout]
        self.layout = LayoutType(config, profile, width)

    def process_line(self, line):
        formatted = self.layout.layout(line.strip())
        if formatted:
            print formatted

for member in inspect.getmembers(logcatcolor.layout):
    LayoutType = member[1]
    if LayoutType == logcatcolor.layout.Layout:
        continue
    if not inspect.isclass(LayoutType):
        continue
    if not logcatcolor.layout.Layout in LayoutType.__bases__:
        continue

    LogcatReader.LAYOUTS[LayoutType.NAME] = LayoutType
