#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name="logcat-color",
      version="0.1",
      description="A colorful alternative to \"adb logcat\"",
      author="Marshall Culpepper",
      author_email="marshall.law@gmail.com",
      url="http://github.com/marshall/logcat-color",
      packages=find_packages(),
      scripts=["logcat-color"],
      install_requires=["colorama"])
