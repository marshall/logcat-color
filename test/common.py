import json
import os

this_dir = os.path.abspath(os.path.dirname(__file__))
top_dir = os.path.dirname(this_dir)
logcat_color = os.path.join(top_dir, "logcat-color")
execfile(logcat_color)

filter_results = os.path.join(this_dir, ".filter_results")
mock_adb = os.path.join(this_dir, "mock-adb")

class MockObject(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

class MockAdbLogcatColor(LogcatColor):
    def __init__(self, log, results, args=None, max_wait_count=None):
        LogcatColor.__init__(self, args=args)
        self.log = log
        self.results = results
        self.wait_count = 0
        self.max_wait_count = max_wait_count

    def get_adb_args(self):
        adb_args = LogcatColor.get_adb_args(self)
        adb_args[0:1] = [mock_adb, "--log", self.log, "--results", self.results]
        return adb_args

    def wait_for_device(self):
        LogcatColor.wait_for_device(self)
        if self.max_wait_count:
            self.wait_count += 1
            if self.wait_count == self.max_wait_count:
                raise KeyboardInterrupt()

def test_filter(fn):
    def wrapped(data):
        result = fn(data)
        save_filter_results(fn.__name__, data, result)
        return result
    return wrapped

def save_filter_results(name, data, result):
    results = read_filter_results()
    if name not in results:
        results[name] = []

    results[name].append({
        "data": data,
        "result": result
    })

    open(filter_results, "w").write(json.dumps(results))

def read_filter_results():
    results = {}
    if os.path.exists(filter_results):
        results = json.loads(open(filter_results, "r").read())

    return results
