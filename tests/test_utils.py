# tests.test_utils
# Testing the hanish utilities module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 09 10:49:05 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_utils.py [] benjamin@bengfort.com $

"""
Testing the hanish utilities module
"""

##########################################################################
## Imports
##########################################################################

import unittest

from hanish.utils import *


##########################################################################
## Decorators Tests
##########################################################################

class DecoratorsTests(unittest.TestCase):
    """
    Basic decorators utility tests.
    """

    def test_memoized(self):
        """
        Test the memoized property
        """

        class Thing(object):

            @memoized
            def attr(self):
                return 42

        thing = Thing()
        self.assertFalse(hasattr(thing, '_attr'))
        self.assertEqual(thing.attr, 42)
        self.assertTrue(hasattr(thing, '_attr'))
