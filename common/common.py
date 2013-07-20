#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig()


def get_logger(name, debug=False):

    # Logger initialization
    app_logger = logging.getLogger(name)

    if debug:
        app_logger.setLevel(logging.DEBUG)
    else:
        app_logger.setLevel(logging.INFO)

    return app_logger


def get_file_logger(name, filename="myhome"):

    # Logger initialization
    app_logger = logging.getLogger(name)
    app_logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.FileHandler("logs/%s.log" % filename)
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

    return app_logger
