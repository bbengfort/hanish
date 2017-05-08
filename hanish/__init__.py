# hanish
# Provides the core functionality for the hanish weatherbot.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon May 08 11:07:14 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
The hanish library provides the core functionality for the hanish weatherbot.
"""

##########################################################################
## Imports
##########################################################################

from .version import get_version, __version_info__


##########################################################################
## Package Version
##########################################################################

__version__ = get_version(short=True)
