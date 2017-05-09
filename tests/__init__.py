# tests
# Testing module for the hanish weather chatbot application.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 11:01:26 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Testing module for the hanish weather chatbot application.
"""

##########################################################################
## Imports and Module Vars
##########################################################################

import unittest


EXPECTED_VERSION = "0.1"


##########################################################################
## Initialization Tests
##########################################################################


class InitializationTests(unittest.TestCase):

    def test_sanity(self):
        """
        Assert the world is sane and that tests will work; 2+2 = 4
        """
        self.assertEqual(2+2, 4)

    def test_import(self):
        """
        Assert that we can import the hanish library
        """
        try:
            import hanish
        except ImportError:
            self.fail("could not import the hanish library")

    def test_version(self):
        """
        Assert that the test version matches the package version
        """
        import hanish
        self.assertEqual(hanish.__version__, EXPECTED_VERSION)
