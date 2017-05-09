# -*- coding: utf-8 -*-
# tests.test_chat
# Tests responses concerning chats about the weather.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 09 14:55:22 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: tests.test_chat.py [] benjamin@bengfort.com $

"""
Tests responses concerning chats about the weather.
"""

##########################################################################
## Imports
##########################################################################

import json
import unittest

from hanish.chat import *
from .test_darksky import WEATHER


##########################################################################
## Chat Test Cases
##########################################################################

class ChatTests(unittest.TestCase):

    def setUp(self):
        with open(WEATHER, 'r') as f:
            self.weather = json.load(f)
            self.weather["zipcode"] = 90210
            self.weather["api_calls"] = 15

    def tearDown(self):
        self.weather = None

    def test_weather_currently(self):
        """
        Test the response to weather now
        """
        expected = (
            u"Currently in 90210 it is 54.4°F and mostly cloudy. "
            u"It will be mostly cloudy throughout the day."
        )
        self.assertEqual(
            weather_currently(self.weather), expected
        )

    def test_weather_tomorrow(self):
        """
        Test the response to weather tomorrow
        """
        expected = (
            u"Light rain on Sunday and Monday, with "
            u"temperatures rising to 62°F on Wednesday."
        )
        self.assertEqual(
            weather_tomorrow(self.weather), expected
        )
