# hanish.exceptions
# Exceptions hierarchy for the hanish application.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 12:44:41 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exceptions hierarchy for the hanish application.
"""

##########################################################################
## Exception Hierarchy
##########################################################################

class HanishException(Exception):
    """
    Top level hanish application-specific exception.
    """
    pass


class ImproperlyConfigured(HanishException):
    """
    A required environment or configuration value was not provided.
    """
    pass


class HanishTypeError(HanishException, TypeError):
    """
    Unexpected hanish application-specifich type.
    """
    pass


class HanishValueError(HanishException, ValueError):
    """
    Unexpected hanish application-specifich value.
    """
    pass


class DatabaseError(HanishException):
    """
    Something went wrong with a hanish database.
    """
    pass


class DarkSkyException(HanishException):
    """
    Something went wrong accessing the Dark Sky API.
    """
    pass
