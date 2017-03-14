from common import *
from logcatcolor.column import *
from logcatcolor.config import *
from logcatcolor.layout import *
from logcatcolor.profile import *
from logcatcolor.reader import *
import unittest


class ProfileTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_package_name_filter(self):
        profile = Profile(name = 'package_filt', packages = ['com.example.test'])
        self.assertFalse(profile.include({'message' : 'Start proc com.example.test for activity tw.com.xxxx.android.yyyy/.333Activity: pid=123456 uid=10105 gids={3003}'}))
        self.assertTrue(profile.include({'pid' : '123456', 'message' : 'foo bar'}))

    def test_package_name_filter_android_51(self):
        profile = Profile(name = 'package_filt', packages = ['com.example.test'])
        self.assertFalse(profile.include({'message' : 'Start proc 26360:com.example.test/u0a208 for activity tw.com.xxxx.android.yyyy/com.example.test.ui.MainActivity'}))
        self.assertTrue(profile.include({'pid' : '26360', 'message' : 'foo bar'}))

    def test_empty_package_will_still_work(self):
        profile = Profile(name = 'package_filt')
        self.assertTrue(profile.include({'message' : 'Start proc com.example.test for activity tw.com.xxxx.android.yyyy/.333Activity: pid=123456 uid=10105 gids={3003}'}))
