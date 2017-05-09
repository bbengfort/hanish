#!/usr/bin/env python
# hanishbot
# Primary entry point and application runner for the Hanish bot.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 11:15:40 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: hanishbot.py [] benjamin@bengfort.com $

"""
Primary entry point and application runner for the Hanish bot.
"""

##########################################################################
## Imports
##########################################################################

import time
import dotenv
import hanish
import argparse


##########################################################################
## Command Arguments
##########################################################################

LOAD_DOTENV = True
DESCRIPTION = "A slackbot that makes small talk about the weather."
VERSION = "hanishbot v{}".format(hanish.get_version())
EPILOG = "Please report bugs or issues to github.com/bbengfort/hanish"


##########################################################################
## Command Functionality
##########################################################################

def chat(args):
    """
    Sends a single debug chat message to the bot and gets a response.
    """

    # TODO: Don't hack this together, but do something a bit better.
    # Closure to monkey-patch bot to print instead of post to Slack.
    def console_post(channel, message):
        print(message)

    # Create at patch the bot
    bot = hanish.Bot()
    bot.post = console_post

    # Create the message
    msg = {
        'ts': time.time(),
        'channel': 'console',
        'text': ' '.join(args.message),
    }

    # Handle the message 
    bot.handle_message(msg)


def runbot(args):
    """
    Connect to the Slack API and listen for weather queries.
    """
    bot = hanish.Bot()
    bot.run()


##########################################################################
## Main Method
##########################################################################

if __name__ == '__main__':

    # Load the environment from the .env file
    if LOAD_DOTENV:
        dotenv.load_dotenv(dotenv.find_dotenv())

    # Create the command line argument parser and subparsers
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, version=VERSION, epilog=EPILOG,
    )
    subparsers = parser.add_subparsers(title="commands")

    # Add the chat command subparser
    wp = subparsers.add_parser('chat', help='send a chat message to the bot')
    wp.add_argument('message', nargs="+", help='the message to send to the bot')
    wp.set_defaults(func=chat)

    # Add the run command subparser
    rp = subparsers.add_parser('run', help='run the weather chatbot')
    rp.set_defaults(func=runbot)

    # Parse the arguments and execute the command
    args = parser.parse_args()
    try:
        args.func(args)
        parser.exit(0, "")
    except Exception as e:
        parser.error(str(e))
