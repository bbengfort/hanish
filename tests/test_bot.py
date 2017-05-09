# tests.test_bot
# Tests the primary Bot interface for the hanish module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 15:06:46 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_bot.py [] benjamin@bengfort.com $

"""
Tests the primary Bot interface for the hanish module.
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import unittest

try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2
    import mock

from hanish.bot import *
from .test_zipcode import FIXTURES, ZIPCODES


MEMBERS = os.path.join(FIXTURES, "members.json")


##########################################################################
## Hanish Bot Helpers Tests
##########################################################################

class BotHelpersTests(unittest.TestCase):

    def setUp(self):
        # Add some environment variables
        os.environ['HANISH_TEST_FOO'] = 'bar'
        os.environ['HANISH_TEST_PATH'] = '/dev/null'

    def tearDown(self):
        # Remove the environment variables
        os.environ.pop('HANISH_TEST_FOO')
        os.environ.pop('HANISH_TEST_PATH')

    def test_environ_defaults(self):
        """
        Assert default values can be fetched from the environment.
        """

        # Test fixture
        kwargs = {'color': 'red', 'foo': 42}

        # Ensure kwargs overrides environment
        self.assertEqual(42, environ_default(kwargs, 'foo', 'HANISH_TEST_FOO'))

        # Remove kwargs and ensure fetched from environment
        del kwargs['foo']
        self.assertEqual('bar', environ_default(kwargs, 'foo', 'HANISH_TEST_FOO'))

        # Ensure default is fetched from environment
        self.assertEqual('/dev/null', environ_default(kwargs, 'path', 'HANISH_TEST_PATH'))

        # Ensure value is fetched with no environment counter part
        self.assertEqual('red', environ_default(kwargs, 'color', 'HANISH_TEST_COLOR'))

    def test_environ_defaults_required(self):
        """
        Assert that required variables raise an exception.
        """
        try:
            environ_default({}, 'notakey', 'HANISH_TEST_NO_KEY_EXISTS', required=False)
        except ImproperlyConfigured:
            self.fail("unrequired key raised a configuration exception")

        with self.assertRaises(ImproperlyConfigured):
            environ_default({}, 'notakey', 'HANISH_TEST_NO_KEY_EXISTS', required=True)


##########################################################################
## Hanish Bot Tests
##########################################################################

class BotTests(unittest.TestCase):

    # Test environment fixtures to configure the bot.
    ENVIRON = {
        "SLACK_BOT_NAME": "hanishbot",
        "SLACK_ACCESS_TOKEN": "test-123456790abc-def1234567890abcdef12345",
        "DARKSKY_ACCESS_TOKEN": "0123456789abcdef9876543210fedcba",
        "DEFAULT_ZIP_CODE": "20001",
        "ZIPCODE_DATABASE": ZIPCODES,
    }

    def setUp(self):
        """
        Modify the environment to configure the bot.
        """
        # Store the original environment
        self.orig_environ = {}

        # Add the test fixtures environment
        for key, val in self.ENVIRON.items():
            # Save the original key
            self.orig_environ[key] = os.environ.get(key, None)

            # Add the fixture to the environment
            os.environ[key] = val

    def tearDown(self):
        """
        Reset the environment configuration.
        """
        for key, val in self.orig_environ.items():
            if val:
                os.environ[key] = val
            else:
                del os.environ[key]

    def test_config_bot(self):
        """
        Assert that a bot is configured from the environment
        """
        bot = Bot()
        self.assertEqual(bot.name, self.ENVIRON['SLACK_BOT_NAME'])
        self.assertEqual(bot.zipcode, self.ENVIRON['DEFAULT_ZIP_CODE'])
        self.assertEqual(bot.darksky.apikey, self.ENVIRON['DARKSKY_ACCESS_TOKEN'])
        self.assertEqual(bot.slack.token, self.ENVIRON['SLACK_ACCESS_TOKEN'])
        self.assertEqual(bot.zipdb.count(), 33144)

    def test_bot_commands_parsing(self):
        """
        Test the command parsing on a variety of correct command strings
        """

        # TODO: Refactor commands into its own module and tests
        commands = Bot().commands

        # Closure that asserts the text matches the given command name.
        def assertCommandMatch(name, text):
            msg = "unparseable {} command: '{}'".format(name, text)
            self.assertIsNotNone(
                commands[name].search(text), msg
            )

        # Test table for commands
        table = (
            ('weather', '<@U1234ABCD> weather now'),
            ('weather', '<@U1234ABCD> weather tomorrow'),
            ('weather', 'weather now <@U1234ABCD>'),
            ('weather', 'weather tomorrow <@U1234ABCD>'),
            ('weather', '<@U1234ABCD> Weather Now'),
            ('weather', '<@U1234ABCD> WEATHER tomorrow'),
            ('weather', 'WEATHER NOW <@U1234ABCD>'),
            ('weather', 'weather    TOMORROW   '),
            ('weather', '<@U1234ABCD> weather now weather tomorrow weather in 98021 darksky limit'),
            ('weather', '<@U1234ABCD> weather now weather now'),
            ('weather', '<@U1234ABCD> weather tomorrow unless you are tired then nevermind'),
            ('location', '<@U1234ABCD> weather in 58054'),
            ('location', 'weather in 20742 <@U1234ABCD>'),
            ('location', '<@U1234ABCD> WEATHER IN 58054'),
            ('location', '<@U1234ABCD> Weather In 58054'),
            ('location', '<@U1234ABCD>   weather    in    58054 other stuff'),
            ('location', '<@U1234ABCD> weather now weather tomorrow weather in 98021 darksky limit'),
            ('darksky', '<@U1234ABCD> darksky limit'),
            ('darksky', 'darksky limit <@U1234ABCD>'),
            ('darksky', '<@U1234ABCD> DARKSKY LIMIT'),
            ('darksky', '<@U1234ABCD> Darksky Limit'),
            ('darksky', '  <@U1234ABCD>    darksky     limit   '),
            ('darksky', '<@U1234ABCD> darksky limit with other stuff at the end'),
            ('darksky', '<@U1234ABCD> weather now weather tomorrow weather in 98021 darksky limit'),
        )

        for name, text in table:
            assertCommandMatch(name, text)

    def test_botid_property(self):
        """
        Test the botid search and atbotid filters
        """
        # Create the bot
        bot = Bot()

        # Mock the slack client
        with open(MEMBERS, 'r') as f:
            members = json.load(f)
        bot.slack.api_call = mock.MagicMock(return_value=members)

        # Test the botid
        self.assertEqual(bot.botid, 'UTEST3210')
        bot.slack.api_call.assert_called_once_with('users.list')

        # Test memoization (second call does not go to API)
        self.assertEqual(bot.botid, 'UTEST3210')
        bot.slack.api_call.assert_called_once_with('users.list')

        # Test atbotid filter
        table = (
            "hello <@UTEST3210>!",
            "<@UTEST3210> weather now",
            "weather now <@UTEST3210>",
        )

        for msg in table:
            self.assertIsNotNone(bot.atbotid.search(msg))
