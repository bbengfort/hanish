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
## Main Method
##########################################################################

if __name__ == '__main__':

    # Load the environment from the .env file
    if LOAD_DOTENV:
        dotenv.load_dotenv(dotenv.find_dotenv())

    # Create the command line argument parser
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, version=VERSION, epilog=EPILOG,
    )

    # Parse the arguments and execute the command
    args = parser.parse_args()
    try:
        print("stub implementation")
        parser.exit(0)
    except Exception as e:
        parser.error(str(e))
