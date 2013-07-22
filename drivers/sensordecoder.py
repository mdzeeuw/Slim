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

    def initialize(self, debug=False):

        self.running = False

        # Regular logger
        if debug:
            self.logger = common.common.get_logger(self.NAME, True)
        else:
            self.logger = common.common.get_file_logger(self.NAME, False)

        # Initalize mqtt client
        self.client = common.mqtt.MQTTClient(self.NAME)
        self.client.connect()

        # Get the packets setup
        self.packets = load_packet_setup()

        self.unknown = []

        self.logger.info("Initialized")
        return True

    def start(self):

        self.logger.info("Starting")
        self.running = True

        # Listen to incomming commands
        self.client.subscribe('command/{0}'.format(self.NAME.lower()), self.receiveCommand)

        self.logger.info("Running")

        # Notify the system we started
        self.client.send("event/{0}/started".format(self.NAME.lower()), self.NAME)

        self.client.subscribe('sensor-raw/#', self.handleData)

        # Run for close to ever
        try:
            while self.running:
                time.sleep(0.5)

                if not self.client.alive:
                    self.logger.error("Client disconnected unexpectedly")
                    break

        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Received external (keyboard) exit")
        except (Exception, e):
            self.logger.error(e)
        finally:
            pass

        self.logger.info("Run loop ended")

        self.stop()

    def handleData(self, message):

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

    def receiveCommand(self, message):

        self.logger.info("Received command: {0}".format(message))

        if message.payload == "stop":
            self.stop()

        if message.payload == "restart":
            self.restart()

    def stop(self):
        if not self.running:
            return

        self.logger.info("Stopping")

        self.running = False

         # Stopped
        self.logger.info("Closing connections")

        # Notify the system we stopped
        self.client.send("event/{0}/stopped".format(self.NAME.lower()), self.NAME)

        # Disconnect from mqtt
        self.client.disconnect()

        self.logger.debug("Awaiting disconnect")
        for i in range(50):
            if not self.client.connected:
                break

            time.sleep(0.1)

        return True

    def restart(self):
        self.logger.info("Restarting")
        return True

    def message(self, message):
        return True

    def getUptime(colName):
        """Get a column of ps output as a list"""
        ps = subprocess.Popen(["uptime"], stdout=subprocess.PIPE)
        (stdout, stderr) = ps.communicate()
        data = stdout.strip()
        return data
