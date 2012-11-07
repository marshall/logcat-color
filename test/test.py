#!/usr/bin/env python
import os
import sys
import unittest

this_dir = os.path.dirname(os.path.abspath(__file__))
logcat_color_dir = os.path.dirname(this_dir)
sys.path.append(logcat_color_dir)

from layout_test import *

if __name__ == "__main__":
    unittest.main()
