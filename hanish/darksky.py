# hanish.darksky
# Handlers and functionality for making Dark Sky API requests.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 12:04:11 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: cdarksky.py [] benjamin@bengfort.com $

"""
Handlers and functionality for making Dark Sky API requests.
"""

##########################################################################
## Imports and Module Vars
##########################################################################

import requests

try:
    # Python 3
    from urllib.parse import urljoin
except ImportError:
    # Python 2
    from urlparse import urljoin


from datetime import date, datetime
from expiringdict import ExpiringDict
from .exceptions import HanishValueError
from .exceptions import DarkSkyException


DARKSKY_API_URL  = "https://api.darksky.net"
API_CALLS_HEADER = "X-Forecast-API-Calls"


##########################################################################
## DarkSky API
##########################################################################

class DarkSky(object):
    """
    The Dark Sky API object maintains its state of API credentials, number of
    requests per session, as well as the last time a query was made (cacheing
    duplicate requests that occur within 5 minutes of each other). Currently,
    only a portion of the available API methods are implemented, namely the
    ``forecast`` method, but can be easily extended in the future.

    Parameters
    ----------
    apikey: string
        The API key obtained from the Dark Sky developers service.

    limit: int or None, default = 1000
        Set a limit to the number of requests made per day. The limit is
        checked via the X-Forecast-API-Calls header made in API responses,
        therefore a single request per process will always be made before the
        limit can be observed.

    cache: time in seconds or None, default = 300
        Cache requests to a specific zipcode for a specific time limit, to
        reduce lookups and rate limit queries to the Dark Sky service.
    """

    def __init__(self, apikey, limit=1000, cache=300):
        self.apikey      = apikey  # API Key included in each request
        self.limit       = limit   # Per-day limit (can be None)
        self.n_api_calls = 0       # Reported number of API queries made
        self.last_query  = None    # Datetime of the last query made
        self.cache_timeout = cache # Age in seconds of values in the cache

        # TODO: Create a cache data structure that implements similar
        # functionality to ``ExpiringDict`` as an internal utility that has no
        # limit and deals with zip codes and method responses specificially.
        # Cache is a third party utility, ExpiringDict, which we use here for
        # speed of development, but should implement ourselves in the future.
        self.cache = ExpiringDict(max_len=limit, max_age_seconds=cache or 0)

    def forecast(self, lat, lon,
                 exclude=None, extend=False, lang="en", units="auto"):
        """
        Performs a cached lookup of the forecast for the given latitude and
        longitude. If the coordinates are in the cache and not expired, then
        that value is returned. Otherwise a request is made to the Dark Sky
        API. Note that changes in query arguments do not modify the cache.

        Parameters
        ----------
        lat,lon: float
            The geo-coordinates to get the forecast for.

        exclude: list
            Exclude some data blocks from the response. The list can contain
            currently, minutely, hourly, daily, alerts, and flags.

        extend: bool, default=False
            If true, return hour-by-hour data for next 168 hours.

        lang: string, default="en"
            The language and locale of the response.

        units: string, default="auto"
            Specify the weather condition units. Can be one of auto, ca, uk2,
            us, and si. The default is auto which selects units based on the
            specified location or language.

        Returns
        -------
        data: json
            The parsed json response of the API query.
        """
        # Use the cached response if it's available and timeout is specified.
        if self.cache_timeout:
            data = self.cache.get((lat,lon))
            if data is not None:
                return data

        # Create the query params
        query = {
            "lang": lang,
            "units": units,
        }

        # Convert the exclude list into the correct format
        if exclude is not None:
            query["exclude"] = ",".join(exclude)

        # Convert the extend bool into the correct format
        if extend:
            query["extend"] = "hourly"

        # Perform the query to the Dark Sky API
        # TODO: use safer method than simple string formatting
        endpoint = "/forecast/{}/{},{}".format(self.apikey, lat, lon)
        data = self.request(endpoint, **query)

        # Cache the result and return
        if self.cache_timeout:
            self.cache[(lat,lon)] = data

        return data

    def request(self, endpoint, **query):
        """
        Performs a GET request by joining the provided endpoint with the API
        url and encoding and attatching the query params provided as generic
        keyword arguments. This function also tracks the number of calls made
        to the API as reported by the X-Forecast-API-Calls header from the
        server, preventing additional requests if the limit is reached.

        Note: This method performs no cacheing and will always make a request
              if under the per-day limit. This method will also raise an
              exception for the HTTP status (e.g. 404, 403, etc.)

        Parameters
        ----------
        endpoint: string
            Path to the Dark Sky api resource, not the full URL

        query: dict
            Dictionary of HTTP query arguments to encode and request

        Returns
        -------
        data: json
            The parsed json response of the API query.
        """

        if self.limit is not None and self.n_api_calls > self.limit:
            raise DarkSkyException(
                "api query limit of {} requests reached".format(self.limit)
            )

        # Join the endpoint with the URL
        url = urljoin(DARKSKY_API_URL, endpoint)

        # Ensure that we'll accept compressed JSON to reduce bandwidth
        headers = {'Accept-Encoding': 'gzip'}

        # Perform the query, raising an exception for non-200 status
        r = requests.get(url, params=query, headers=headers)
        r.raise_for_status()

        # Get the X-Forecast-API-Calls header
        if API_CALLS_HEADER in r.headers:
            self.n_api_calls = int(r.headers[API_CALLS_HEADER])

        # Return the parsed JSON data
        return r.json()
