# hanish.utils
# Decorators and package utilities.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 09 10:47:59 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: utils.py [] benjamin@bengfort.com $

"""
Decorators and package utilities.
"""

##########################################################################
## Imports
##########################################################################

from functools import wraps


##########################################################################
## Memoization
##########################################################################

def memoized(fget):
    """
    Return a property attribute for new-style classes that only calls its
    getter on the first access. The result is stored and on subsequent
    accesses is returned, preventing the need to call the getter any more.
    https://github.com/estebistec/python-memoized-property
    """
    attr_name = '_{0}'.format(fget.__name__)

    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)
