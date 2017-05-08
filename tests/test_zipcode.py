# tests.test_zipcode
# Test the zipcode to latitutide,longitude lookup database.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 12:35:21 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_zipcode.py [] benjamin@bengfort.com $

"""
Test the zipcode to latitutide,longitude lookup database.
"""

##########################################################################
## Imports and Fixtures
##########################################################################

import os
import unittest

from hanish.zipcode import ZipCodeDB
from hanish.exceptions import HanishValueError


FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")
ZIPCODES = os.path.join(FIXTURES, "ziplatlon.csv")


##########################################################################
## ZipCodeDB Tests
##########################################################################

class ZipCodeDBTests(unittest.TestCase):

    def test_database_loading_lookup_and_close(self):
        """
        Integration test for loading and looking up zipcodes
        """
        zipdb = ZipCodeDB.load(ZIPCODES)

        table = (
            ('20001', (38.910353, -77.017739)),
            ('58054', (46.416876, -97.668726)),
            ('94020', (37.274612, -122.23242)),
            ('20742', (38.989619, -76.945695)),
            ('98201', (48.006311, -122.210044)),
            ('10706', (40.989821, -73.867552)),
            ('02124', (42.285805, -71.070571)),
        )

        for zipcode, expected in table:
            self.assertEqual(expected, zipdb.lookup(zipcode))

        zipdb.close()
        self.assertIsNone(zipdb.conn, "database not closed correctly")

    def test_unloaded_database_and_not_found(self):
        """
        Test zipcode database behavior when not loaded or not found
        """
        zipdb = ZipCodeDB()

        table = (
            ('20001', (38.910353, -77.017739)),
            ('58054', (46.416876, -97.668726)),
            ('94020', (37.274612, -122.23242)),
            ('20742', (38.989619, -76.945695)),
            ('notazip', (15.0000, 70.00000)),
        )

        for zipcode, _ in table:
            with self.assertRaises(HanishValueError):
                zipdb.lookup(zipcode)
