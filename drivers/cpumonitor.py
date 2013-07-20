#!/usr/bin/env python
# -*- coding: utf-8 -*-

import driver
import common.config
import common.error
import common.common
import common.mqtt

import subprocess
import time


class CPUMonitor(driver.Driver):

    CHECK_INTERVAL = 60

    def initialize(self):

        self.running = False

        # Regular logger
        self.logger = common.common.get_logger("CPUMonitor", True)

        # Initalize mqtt client
        self.client = common.mqtt.MQTTClient("CPUMonitor")
        self.client.connect()

        self.logger.info("Initialized")
        return True

    def start(self):

        self.logger.info("Starting")
        self.running = True

        # Listen to incomming commands
        self.client.subscribe('commands/cpumonitor', self.receiveCommand)

        self.logger.info("Running")

        # Notify the system we started
        self.client.send("events/driver/started", "CPU Monitor")

        last_check_time = None

        # Run for close to ever
        try:
            while self.running:
                self.logger.debug("cpu loop")
                if last_check_time is None or time.time() - last_check_time > self.CHECK_INTERVAL:
                    data = self.getUptime()

                    self.handleData(data)
                    last_check_time = time.time()

                time.sleep(0.5)
        finally:
            pass

        self.logger.info("Run loop ended")

        self.stop()

    def handleData(self, data):

        self.logger.debug("Got data {0}".format(data))

        parsed = data.split(' ')

        #print parsed

        #print len(parsed)

        if len(parsed) == 13:
            uptime = parsed[3].strip(' ,')
            users = parsed[5].strip(' ,')
            cpu_1 = parsed[10].strip(' ,')
            cpu_5 = parsed[11].strip(' ,')
            cpu_15 = parsed[12].strip(' ,')

            self.logger.debug("CPU. up {0} users {1} cpu1 {2} cpu5 {3} cpu15 {4}".format(uptime, users, cpu_1, cpu_5, cpu_15))

            self.client.send("sensor/0/pigate/uptime", uptime)
            self.client.send("sensor/0/pigate/users", users)
            self.client.send("sensor/0/pigate/cpu_load_1m", cpu_1)
            self.client.send("sensor/0/pigate/cpu_load_5m", cpu_5)
            self.client.send("sensor/0/pigate/cpu_load_15m", cpu_15)

        # Send the raw data over mqtt
        #self.client.send("sensor-raw/0/cpu", data)

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
        self.client.send("events/driver/stopped", "CPU Monitor")

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
