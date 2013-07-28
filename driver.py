#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Myhome Driver Abstract
"""

import common.config
import common.error
import common.common
import common.mqtt

import time


class Driver(object):

    logger = None
    NAME = "DriverAbstract"

    def initialize(self, debug=False):

        self.running = False

        # Regular logger
        if debug:
            self.logger = common.common.get_logger(self.NAME, True)
        else:
            self.logger = common.common.get_file_logger(self.NAME, False)

        # Initalize mqtt client
        self.client = common.mqtt.MQTTClient(self.NAME, debug)

        self.client.client.will_set("event/{0}/died".format(self.NAME.lower()), self.NAME)

        self.client.connect()

        if not self.client.connected:
            self.logger.error("Failed to connect to the MQTT broker")
            self.client.kill()
            return False

        self.load()

        self.logger.info("Initialized")
        return True

    def load(self):
        pass

    def start(self):

        self.logger.info("Starting")
        self.running = True

        # Listen to incomming commands
        self.client.subscribe('command/{0}'.format(self.NAME.lower()), self.receiveCommand)

        self.logger.info("Running")

        # Notify the system we started
        self.client.send("event/{0}/started".format(self.NAME.lower()), str(time.time()), 0, 0, True)

        # Run for close to ever
        try:
            while self.running:

                if not self.client.alive:
                    raise Exception("Client disconnected unexpectedly")

                self.run()

                time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Received external (keyboard) exit")

        except Exception as e:
            self.logger.error(e)

            self.client.send("event/{0}/error".format(self.NAME.lower()), str(e), 0, 0, True)

        finally:
            self.logger.info("Run loop ended")
            self.stop()

    def run(self):
        raise DriverException("Run is not implemented")

    def receiveCommand(self, message):

        self.logger.info("Received command: {0}".format(message))

        if message.payload == "stop":
            self.running = False

        if message.payload == "restart":
            self.restart()

    def stop(self):

        self.logger.info("Stopping")

        self.running = False

         # Stopped
        self.logger.info("Closing connections")

        # Notify the system we stopped
        self.client.send("event/{0}/stopped".format(self.NAME.lower()), str(time.time()))

        # Disconnect from mqtt
        self.client.disconnect()

        self.logger.debug("Awaiting disconnect")
        for i in range(50):
            if not self.client.connected:
                break

            time.sleep(0.1)

        self.logger.debug("Awaiting looper stop")
        for i in range(50):
            if not self.client.alive:
                break

            time.sleep(0.1)

        return True

    def restart(self):
        raise DriverException("Restart is not implemented")

    def message(self, message):
        raise DriverException("Message is not implemented")


class DriverException(common.error.MyHomeException):
    pass
