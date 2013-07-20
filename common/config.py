#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Config loader
"""

import yaml
import yaml.scanner

import error


def getConfig(file):

    return Config(file)


class Config():

    def __init__(self, filename):

        try:
            with open('config/%s.yml' % filename, 'r') as h:

                self.data = yaml.load(h)

                h.close()

                return
        except yaml.scanner.ScannerError:
            raise ConfigError("Invalid config file '{0}'".format(filename))

        return

    def get(self, item, default=None):

        if item in self.data:
            return self.data[item]

        else:
            return default


class ConfigError(error.MyHomeException):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
