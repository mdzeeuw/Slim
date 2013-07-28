#!/usr/bin/env python
# -*- coding: utf-8 -*-

import driver
import common.config
import common.error
import common.common
import common.mqtt

import subprocess
import time

from config.sensors import load_packet_setup
from struct import *


class SensorDecoder(driver.Driver):

    NAME = "SensorDecoder"

    CHECK_INTERVAL = 60

    unknown = None

    def load(self):
        # Get the packets setup
        self.packets = load_packet_setup()

        self.unknown = []

        self.client.subscribe('sensor-raw/#', self.handleData)

        self.logger.info("Loaded")

        return True

    def run(self):
        pass

    def handleData(self, message):
        if not self.running:
            return

        self.logger.debug("Got data {0}".format(message.topic))

        data = message.payload.split(' ')

        if len(data) < 4:
            self.logger.debug("Got invalid data")
            return

        group = int(data.pop(0))
        node = int(data.pop(0))
        type = int(data.pop(0))

        bytes = ""

        for i in data:
            bytes = bytes + pack('B', int(i))

        if type in self.packets:
            parsed = self.packets[type].decode(bytes)

            for (meas, value) in parsed.items():
                self.client.send("sensor/{0}/{1}/{2}/{3}".format(group, node, type, meas), str(value), True)

            self.client.send("sensor/{0}/{1}/{2}/timestamp".format(group, node, type), str(int(time.time())), True)

        else:

            if not type in self.unknown:
                self.unkown.push(type)
                self.log.error("Fail {0} - {1} - {2}".format(group, node, type))
                self.log.error(data)

    def restart(self):
        self.logger.info("Restarting")
        return True

    def message(self, message):
        return True
