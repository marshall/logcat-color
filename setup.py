#!/usr/bin/env python
"""
logcat-color

Copyright 2012-2013, Marshall Culpepper
Licensed under the Apache License, Version 2.0
"""
import codecs
import json
from setuptools import setup, find_packages

setup_data = json.load(open("setup.json", "r"))

# real classy distutils, name / version have to be ascii encoded :(
for ascii_key in ("name", "version"):
    setup_data[ascii_key] = setup_data[ascii_key].encode("ascii")

setup_data["packages"] = find_packages()
setup(**setup_data)
