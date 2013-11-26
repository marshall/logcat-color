#!/usr/bin/env python
"""
logcat-color

Copyright 2012-2013, Marshall Culpepper
Licensed under the Apache License, Version 2.0
"""
import os
import sys
import unittest

this_dir = os.path.dirname(os.path.abspath(__file__))
logcat_color_dir = os.path.dirname(this_dir)
sys.path.append(logcat_color_dir)

from format_test import *
from config_test import *
from logcat_color_test import *
from profile_test import *

if __name__ == "__main__":
    unittest.main()
