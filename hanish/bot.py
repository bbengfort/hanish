# hanish.bot
# Primary interface to the hanish Slack bot.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 14:44:06 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: bot.py [] benjamin@bengfort.com $

"""
Primary interface to the hanish Slack bot. The bot listens for chat messages
and responds appropriately, also looking up weather by zip code.
"""

##########################################################################
## Imports
##########################################################################

import os
import json

from .exceptions import *
from .darksky import DarkSky
from .zipcode import ZipCodeDB


##########################################################################
## Helper Functions
##########################################################################

def environ_default(kwargs, name, envvar, default=None, required=False):
    """
    This helper function fetches a default value from the specified envvar if
    the name doesn't exist in the kwargs dictionary. If the name or envvar are
    not defined, then this function returns the default value unles required
    is True, at which point an ImproperlyConfigured exception is raised.
    """

    # If the name is in the keyword arguments, return its value
    if name in kwargs: return kwargs[name]

    # If the envvar is in the environment, return its value.
    if envvar in os.environ: return os.environ[envvar]

    # If required is True and we're here, raise an exception.
    if required:
        raise ImproperlyConfigured(
            "Required config {} not found in ${}".format(name, envvar)
        )

    # Otherwise return the default
    return default


##########################################################################
## Hanish Bot
##########################################################################

class Bot(object):
    """
    A Bot encapsulates the behavior and functionality of Hanish slackbot,
    allowing it to query the Dark Sky weather service, lookup geo-coordinates
    by zip code and to listen for and respond to messages from users on Slack.

    The Bot is configured primarily from environment variables, though every
    configuration parameter can be overriden in the constructor. However, for
    normal usage, it is preferred that configuration is stored in the env.

    Parameters
    ----------
    name: string, environment: $SLACK_BOT_NAME
        The name of the slackbot identified in Slack chat.

    slack_api_key: string, environment: $SLACK_ACCESS_TOKEN
        The api token to access the Slack API, starts with "xoxb-"

    darksky_api_key: string, environment: $DARKSKY_ACCESS_TOKEN
        The api token to access the Dark Sky API

    default_zip: string, environment: $DEFAULT_ZIP_CODE
        The default zip code to use when making lookups

    zipcodes: string, environment: $ZIPCODE_DATABASE
        Path to the zip codes database CSV file.
    """

    def __init__(self, **config):
        # NOTE: Normally PEP8 requires breaks at 78 chars, but longer here so
        # that I can more quickly see the configurations and variable names.
        # Get app properties from the configuration.
        self.name = environ_default(config, "name", "SLACK_BOT_NAME", "hanish")
        self.zipcode = environ_default(config, "default_zip", "DEFAULT_ZIP_CODE", "20001")

        # Create the zip codes database
        zipcodes = environ_default(config, "zipcodes", "ZIPCODE_DATABASE", "fixtures/ziplatlon.csv")
        self.zipdb = ZipCodeDB.load(zipcodes)

        # Initialize the Dark Sky API
        darksky_api_key = environ_default(config, "darksky_api_key", "DARKSKY_ACCESS_TOKEN", required=True)
        self.darksky = DarkSky(darksky_api_key)

        # Initialize the Slack API
        slack_api_key = environ_default(config, "slack_api_key", "SLACK_ACCESS_TOKEN", required=True)
        # self.slack = SlackClient(slack_api_key)

    def weather(self, zipcode=None):
        """
        Quick lookup of the current weather for a given zipcode. If no zipcode
        is supplied, then will look up the weather for the default zipcode.

        Parameters
        ----------
        zipcode: string, default None
            Zip Code to lookup weather for or None for the default

        Returns
        -------
        data: json
            Prints a nicely idented summary of the weather

        msg: string
            Returns a string of the number of dark sky api calls made.
        """
        zipcode  = zipcode or self.zipcode
        lat, lon = self.zipdb.lookup(zipcode)
        forecast = self.darksky.forecast(lat, lon)

        # TODO: simply return the weather in JSON and let the CLI handle print
        weather  = forecast['currently']
        weather['zipcode'] = zipcode
        print(json.dumps(weather, indent=2))
        return "{} Dark Sky API calls made today".format(self.darksky.n_api_calls)
