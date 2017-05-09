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

See also: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""

##########################################################################
## Imports
##########################################################################

import os
import re
import json
import time
import signal
import schedule

from .chat import *
from .exceptions import *
from .utils import memoized
from .darksky import DarkSky
from .zipcode import ZipCodeDB
from slackclient import SlackClient

# time to wait between websocket reads
POLLING_INTERVAL = 1


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
        # Holds the weather for yesterday to check if things have changed.
        self.yesterday = None

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
        self.slack  = SlackClient(slack_api_key)

    @memoized
    def commands(self):
        """
        This property compiles regular expressions for the commands that are
        parsed from messages that are @ mentioned to the bot. Currently
        implemented commands are:

            - weather (now|tomorrow)
            - weather in (zipcode)
            - darksky limit

        The @botid can appear either before or after the command, and multiple
        commands can be included per line. The only rule is that the command
        syntax is unbroken except by white space.

        All commands are case insensitive.
        """
        # TODO: Refactor commands into their own module since I decoupled the
        # command from the @botid string (which is why it was here originally)
        return {
            'weather': re.compile(r'weather\s+(now|tomorrow)', re.I),
            'location': re.compile(r'weather\s+in\s+(\d{5})', re.I),
            'darksky': re.compile(r'darksky\s+limit', re.I),
        }

    @memoized
    def botid(self):
        """
        Looks up the bot id by name from the users list, then memoizes it.
        """

        # Look up the bot id from the users list
        resp = self.slack.api_call("users.list")
        if resp.get("ok"):
            # Retrieve the users and find the bot
            for member in resp.get("members"):
                if 'name' in member and member.get('name') == self.name:
                    return member.get('id')

        # If we get this far without a botid, we have a problem.
        raise SlackException(
            "could not find an ID for a bot named {}".format(self.name)
        )

    @memoized
    def atbotid(self):
        """
        Computes and memoizes the @botid regular expression for directed
        messages that may contain commands. E.g. the pattern for <@botid>.
        """
        return re.compile(
            re.escape("<@{}>".format(self.botid)), re.I
        )

    def run(self):
        """
        Connects to the Slack real-time messaging API, polling every second
        for messages
        """
        # Set up the signal handlers
        # TODO: use threads to better manage communication
        self.shutdown = False
        signal.signal(signal.SIGINT, lambda signal, frame: self.stop())

        # Fetch and cache the current weather at startup
        self.weather()

        # Schedule timed events
        self.set_schedule()

        # Connect to the real time message API
        if self.slack.rtm_connect():
            # TODO: add better chat logging
            print("slackbot named {} ({}) is connected".format(self.name, self.botid))

            while True:

                # Check if we're shutdown
                if self.shutdown:
                    break

                # Check to see if anything has come through the channel
                self.read_rtm_channel()

                # Run any scheduled tasks
                schedule.run_pending()

                # Sleep for a bit until the next time we read the channel
                time.sleep(POLLING_INTERVAL)

        else:
            raise SlackException(
                "could not connect to API: invalid Slack API key or Bot ID?"
            )

        # If we've made it here, we've been shutdown
        # TODO: convert to logging functionality
        print("bot has been gracefully shutdown")

    def stop(self):
        """
        Set the shutdown semaphore
        """
        self.shutdown = True

    def read_rtm_channel(self):
        """
        Reads the RTM channel, parses output, filters messages based on type
        and if they are directed at the bot. If so, passes those messages on
        to the message handler command.
        """

        # Check for messages on the wire
        # TODO: as soon as we connect, the last message comes through.
        messages = self.slack.rtm_read()
        if messages and len(messages) > 0:
            # If there are messages, begin filtering and parsing.
            for msg in messages:
                # Filter only messages from other users
                if msg["type"] == "message":
                    # Check if an @botid appears in the message
                    if self.atbotid.search(msg.get("text", "")):
                        # Handle the atbotid message
                        self.handle_message(msg)

    def handle_message(self, msg):
        """
        Handles messages that are directed at the bot by parsing commands.
        """
        # Log the message received
        # TODO: change to standardized logging functionality
        print("[{}] {}".format(msg["ts"], msg["text"]))

        # Track if an unknown command has occurred
        unknown = True

        # Determine if the message matches any commands
        for name, command in self.commands.items():
            match = command.search(msg["text"])
            if match is not None:
                unknown = False # We've found at least one command match.

                # Get the method that handles this command
                handler = getattr(self, "handle_{}_command".format(name), None)
                if handler is None:
                    raise NotImplementedError(
                        "{} command not yet handled".format(name)
                    )

                try:
                    # Handle the command
                    handler(msg)
                except HanishException as e:
                    # Respond with hanish exceptions
                    response = "Sorry, there was a problem with your request: {}".format(e)
                    self.post(msg['channel'], response)
                except Exception as e:
                    # Fatal exception has occurred
                    self.post(msg['channel'], "A fatal exception has occurred!")

        # Handle any unknown commands
        if unknown:
            self.handle_unknown_command(msg)

    def handle_weather_command(self, msg):
        """
        Have the chatbot respond to the weather command.
        """
        # Parse the weather command arguments
        # NOTE: only the first weather command will be matched
        # TODO: handle all unique weather commands/arguments
        match  = self.commands['weather'].search(msg['text'])
        period = match.group(1).lower()
        weather = self.weather()

        if period == "now":
            response = weather_currently(weather)

        if period == "tomorrow":
            response = weather_tomorrow(weather)

        self.post(msg['channel'], response)

    def handle_location_command(self, msg):
        """
        Have the chatbot respond to the location command.
        """
        # Parse the location command arguments
        for match in self.commands['location'].finditer(msg['text']):
            zipcode = match.group(1)
            weather = self.weather(zipcode)

            response = weather_currently(weather)
            self.post(msg['channel'], response)

    def handle_darksky_command(self, msg):
        """
        Have the chatbot respond to the darksky command.
        """
        response = "I have made {} Dark Sky API calls today.".format(
            self.darksky.n_api_calls
        )
        self.post(msg['channel'], response)

    def handle_unknown_command(self, msg):
        """
        Have the chatbot respond when an unknown command is sent.
        """
        response = (
            "I'm happy to chat about the weather, "
            " unfortunately I don't understand what you're asking."
        )

        self.post(msg['channel'], response)

    def post(self, channel, response):
        """
        Helper function to post a message as the slackbot.
        """
        self.slack.api_call(
            "chat.postMessage", channel=channel, text=response, as_user=True
        )

    def set_schedule(self):
        """
        Sets the schedule to do tasks on demand.
        """
        schedule.every().day.at("9:00").do(self.weather_notice)

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
        # Resolve the latitutde and longitude from the zipcode and query
        # weather. NOTE: this will utilize cacheing on the API if available.
        zipcode  = zipcode or self.zipcode
        lat, lon = self.zipdb.lookup(zipcode)
        forecast = self.darksky.forecast(lat, lon)

        # Add additional information and return
        forecast['zipcode'] = zipcode
        forecast['api_calls'] = self.darksky.n_api_calls
        return forecast

    def weather_notice(self):
        """
        Detects if there is any material change in the weather and alerts the
        channel. This method is scheduled to run every day at 9:00am
        """
        # Keep track if we should alert or not, and get the current weather.
        alert   = False
        weather = self.weather()

        if self.yesterday:
            # Fetch weather for yesterday and today
            current = weather['hourly']['summary']
            yesterday = self.yesterday['hourly']['summary']

            # Detect if there has been a change
            # TODO: Define material change and update accordingly
            if current != yeseterday:
                alert = True
        else:
            alert = True

        # If alert, post a message.
        if alert:
            msg = "Good morning, @channel! A quick update on the weather. "
            msg += weather_currently(weather)
            self.post("#general", msg)

        # Save today's weather for tomorrow
        self.yesterday = weather
