# tests.test_app
# Tests the primary App interface for the hanish module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 15:06:46 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_app.py [] benjamin@bengfort.com $

"""
Tests the primary App interface for the hanish module.
"""

##########################################################################
## Imports
##########################################################################

import os
import unittest

from hanish.app import *


##########################################################################
## Hanish App Tests
##########################################################################

class AppHelpersTests(unittest.TestCase):

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
