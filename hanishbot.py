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

def weather(args):
    """
    Print out the weather for the given zipcode.
    """
    bot = hanish.Bot()
    print(bot.weather(args.zipcode))


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

    # Add the weather command subparser
    wp = subparsers.add_parser('weather', help='quick lookup of the weather')
    wp.add_argument('zipcode', nargs="?", default=None, help='the zipcode to look weather up for')
    wp.set_defaults(func=weather)

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
