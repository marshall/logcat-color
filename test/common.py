import json
import os

this_dir = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.dirname(this_dir)
filter_results = os.path.join(test_dir, ".filter_results")

class MockObject(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

MockColumn = lambda name, def_width: MockObject(NAME=name, DEFAULT_WIDTH=def_width)
MockOptions = lambda config, wrap: MockObject(config=config, wrap=wrap)

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
