"""
logcat-color

Copyright 2012-2013, Marshall Culpepper
Licensed under the Apache License, Version 2.0

Cross platform terminal code
"""
import os
import platform
import struct

# store a large width when the output of this script is being piped
MAX_WIDTH = 2000

class TermWin32(object):
    csbi_struct = 'hhhhHhhhhhh'

    def get_width(self, fd):
        try:
            from colorama import win32
            width = win32.GetConsoleScreenBufferInfo().dwSize.X

            return width or MAX_WIDTH
        except:
            return 80

class TermPosix(object):
    size_struct = 'hh'

    def get_width(self, fd):
        import fcntl, termios
        if not os.isatty(fd):
            return MAX_WIDTH

        # unpack the current terminal width / height
        data = fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
        _, width = struct.unpack(self.size_struct, data)
        return width

if platform.system() == 'Windows':
    _impl = TermWin32()
else:
    _impl = TermPosix()

def get_width(fd):
    return _impl.get_width(fd)
