"""
logcat-color

Copyright 2012, Marshall Culpepper
Licensed under the Apache License, Version 2.0

Logcat I/O stream readers and helpers
"""
import asyncore
import asynchat
import inspect
import os
import sys
import traceback

from cStringIO import StringIO
from subprocess import Popen, PIPE
from threading import Thread, Event
from Queue import Queue, Empty

from logcatcolor.format import Format, detect_format, BriefFormat
from logcatcolor.layout import Layout, BriefLayout

class LineReader(Thread):
    daemon = True

    def __init__(self, file):
        super(LineReader, self).__init__()
        self.file = file
        self.queue = Queue()
        self.event = Event()

    def run(self):
        while True:
            try:
                line = self.file.readline()
                if line == '' or self.event.isSet():
                    break

                self.queue.put(line)
            except KeyboardInterrupt, e:
                break

    def stop(self):
        self.event.set()

class LogcatReader(object):
    DETECT_COUNT = 3

    def __init__(self, config, profile=None, format=None, layout=None,
                 writer=None, width=80):
        self.detect_lines = []
        self.config = config
        self.profile = profile
        self.width = width
        self.writer = writer or sys.stdout

        self.format = None
        if format is not None:
            FormatType = Format.TYPES[format]
            self.format = FormatType()

        self.layout = None
        if layout is not None:
            LayoutType = Layout.TYPES[layout]
            self.layout = LayoutType(config, profile, width)

    def __del__(self):
        # Clear the "detect" lines if we weren't able to detect a format
        if len(self.detect_lines) > 0 and not self.format:
            self.format = BriefFormat()
            if not self.layout:
                self.layout = BriefLayout(self.config, self.profile, self.width)

            for line in self.detect_lines:
                self.layout_line(line)

    def start_logcat(self, command):
        proc = Popen(command, stdout=PIPE)
        try:
            self.start_file(proc.stdout)
        finally:
            if proc.returncode is None:
                proc.terminate()

    def start_file(self, file):
        t = LineReader(file)
        t.start()

        try:
            while t.isAlive() or not t.queue.empty():
                try:
                    line = t.queue.get(True, 0.5)
                    self.process_line(line)
                    t.queue.task_done()
                except Empty, e:
                    continue
        finally:
            if t.isAlive():
                t.stop()

    def detect_format(self, line):
        if len(self.detect_lines) < self.DETECT_COUNT:
            self.detect_lines.append(line)
            return False

        format_name = detect_format(self.detect_lines) or "brief"
        self.format = Format.TYPES[format_name]()
        if not self.layout:
            self.layout = Layout.TYPES[format_name](self.config, self.profile,
                self.width)

        for line in self.detect_lines:
            self.layout_line(line)

        self.detect_lines = []
        return True

    def process_line(self, line):
        line = line.strip()
        if not self.format:
            if not self.detect_format(line):
                return

        self.layout_line(line)

    def layout_line(self, line):
        if Format.MARKER_REGEX.match(line):
            result = self.layout.layout_marker(line)
            if result:
                self.writer.write(result)
            return

        try:
            if not self.format.match(line) or not self.format.include(self.profile):
                return

            result = self.layout.layout_data(self.format.data)
            if not result:
                return

            self.writer.write(result + "\n")
        finally:
            self.format.data.clear()
