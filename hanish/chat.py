# hanish.chat
# Constructs responses to queries from data.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 09 14:54:32 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: chat.py [] benjamin@bengfort.com $

"""
Constructs responses to queries from data.
"""

##########################################################################
## Response formulations
##########################################################################

def weather_currently(weather):
    """
    Returns a string representation of the current weather conditions.
    """
    currently = weather['currently']
    hourly = weather['hourly']
    return (
        u"Currently in {} it is {:0.1f}\u00b0F and {}. "
        u"It will be {}"
    ).format(
        weather['zipcode'], currently['temperature'],
        currently['summary'].lower(), hourly['summary'].lower(),
    )


def weather_tomorrow(weather):
    """
    Returns a string representation of the forecast for tomorrow.
    """
    return weather['daily']['summary']
