#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name, debug=False):

    logging.basicConfig()

    # Logger initialization
    app_logger = logging.getLogger(name)

    if debug:
        app_logger.setLevel(logging.DEBUG)
    else:
        app_logger.setLevel(logging.INFO)

    return app_logger


def get_file_logger(name, debug=False, filename="myhome"):

    # Logger initialization
    app_logger = logging.getLogger(name)
    if debug:
        app_logger.setLevel(logging.DEBUG)
    else:
        app_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.FileHandler("logs/%s.log" % filename)
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

    return app_logger


# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
