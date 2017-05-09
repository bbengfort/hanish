# tests.test_darksky
# Tests for the Dark Sky API handlers.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 15:41:04 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_darksky.py [] benjamin@bengfort.com $

"""
Tests for the Dark Sky API handlers.
"""

##########################################################################
## Imports and Fixtures
##########################################################################

import os
import json
import unittest
import requests_mock

from hanish.darksky import *

try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2
    import mock


FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")
WEATHER  = os.path.join(FIXTURES, "weather.json")

TEST_API_KEY   = "0123456789abcdef9876543210fedcba"
TEST_LATITUDE  = 42.3601
TEST_LONGITUDE = -71.0589


##########################################################################
## Mocking Helper Functions
##########################################################################

def load_fixture(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_weather_json(request, context):
    return load_fixture(WEATHER)


##########################################################################
## Dark Sky API Tests
##########################################################################

@requests_mock.Mocker()
class DarkSkyTests(unittest.TestCase):

    def test_darksky_request(self, m):
        """
        Test the Dark Sky API state as requests are made.
        """
        api = DarkSky(TEST_API_KEY)

        # Create the test endpoints
        endpoint = "/forecast/0123456789abcdef9876543210fedcba/42.3601,-71.0589"
        url = "https://api.darksky.net" + endpoint

        # Mock the request to the URL
        headers = {API_CALLS_HEADER: "42"}
        m.get(url, json=load_weather_json, headers=headers, status_code=200)

        # Check the initial state
        self.assertEqual(api.n_api_calls, 0)

        # Make the request and check it
        data = api.request(endpoint)
        self.assertEqual(api.n_api_calls, 42)
        self.assertEqual(len(data.keys()), 9)

    def test_darksky_limit_observed(self, m):
        """
        Assert that the Dark Sky API raises a limit reached error.
        """
        api = DarkSky(TEST_API_KEY, limit=10)

        # Create the test endpoints
        endpoint = "/forecast/0123456789abcdef9876543210fedcba/42.3601,-71.0589"
        url = "https://api.darksky.net" + endpoint

        # Mock the request to the URL
        headers = {API_CALLS_HEADER: "42"}
        m.get(url, json=load_weather_json, headers=headers, status_code=200)

        # Check the initial state
        self.assertEqual(api.n_api_calls, 0)

        # Make the request and check it -- the first call should work.
        data = api.request(endpoint)
        self.assertEqual(api.n_api_calls, 42)
        self.assertIsNotNone(data)

        # The second request should cause an exception
        with self.assertRaises(DarkSkyException):
            data = api.request(endpoint)
            self.assertEqual(api.n_api_calls, 42)

    def test_forecast_method_with_cacheing(self, m):
        """
        Test the Dark Sky forecast method with cacheing
        """
        # Create the API and mock the request method
        api = DarkSky(TEST_API_KEY, limit=10, cache=3000)
        api.request = mock.MagicMock(return_value=load_fixture(WEATHER))

        # Create the test endpoints
        endpoint = "/forecast/0123456789abcdef9876543210fedcba/42.3601,-71.0589"
        url = "https://api.darksky.net" + endpoint

        # Check the initial state
        self.assertEqual(len(api.cache), 0)

        # Fetch the forecast
        data = api.forecast(TEST_LATITUDE, TEST_LONGITUDE)

        # Test the post-forecast state
        self.assertEqual(len(api.cache), 1)
        self.assertEqual(len(data.keys()), 9)
        api.request.assert_called_once_with(endpoint, lang="en", units="auto")

        # Fetch the forecast a few times and ensure response is cached
        for _ in range(10):
            data = api.forecast(TEST_LATITUDE, TEST_LONGITUDE)
            self.assertEqual(1, len(api.request.mock_calls))

        # Clear the cache and ensure response is called
        api.cache.pop((TEST_LATITUDE,TEST_LONGITUDE))
        data = api.forecast(TEST_LATITUDE, TEST_LONGITUDE)
        self.assertEqual(2, len(api.request.mock_calls))

    def test_forecast_method_without_cacheing(self, m):
        """
        Test the Dark Sky forecast method without cacheing
        """
        # Create the API and mock the request method
        api = DarkSky(TEST_API_KEY, limit=10, cache=None)
        api.request = mock.MagicMock(return_value=load_fixture(WEATHER))

        for idx in range(10):
            data = api.forecast(TEST_LATITUDE, TEST_LONGITUDE)
            self.assertEqual(idx+1, len(api.request.mock_calls))
            self.assertEqual(len(api.cache), 0)
