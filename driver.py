#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Myhome Driver Abstract
"""

import common.error


class Driver():

    logger = None

    def initialize(self):
        raise DriverException("Initialize is not implemented")

    def start(self):
        raise DriverException("Start is not implemented")

    def stop(self):
        raise DriverException("Stop is not implemented")

    def restart(self):
        raise DriverException("Restart is not implemented")

    def message(self, message):
        raise DriverException("Message is not implemented")


class DriverException(common.error.MyHomeException):
    pass
