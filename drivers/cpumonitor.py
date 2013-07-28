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
    NAME = "CPUMonitor"

    last_check_time = None

    def run(self):
        #self.logger.debug("cpu loop")
        if self.last_check_time is None or time.time() - self.last_check_time > self.CHECK_INTERVAL:
            data = self.getUptime()

            self.handleData(data)
            self.last_check_time = time.time()

        time.sleep(0.1)

    def handleData(self, data):

        self.logger.debug("Got data {0}".format(data))

        parsed = data.strip(' \n\r\t').replace('  ', ' ').split(' ')

        #print parsed
        #print len(parsed)
        cpu_15 = None
        # curr time
        if len(parsed):
            ct = parsed.pop(0)

        # 'up'
        if len(parsed):
            parsed.pop(0)

        uptime = ""
        # uptime, last one has ',' at end
        while len(parsed):
            uptime = uptime + " " + parsed.pop(0)

            if uptime[-1] == ',':
                uptime = uptime.strip(' ,')
                break

        # user count
        if len(parsed):
            users = parsed.pop(0).strip(' ,')

        # user text
        if len(parsed):
            parsed.pop(0).strip(' ,')

        # load text
        if len(parsed):
            parsed.pop(0).strip(' ,')

        # average text
        if len(parsed):
            parsed.pop(0).strip(' ,')

        # load_1 text
        if len(parsed):
            cpu_1 = parsed.pop(0).strip(' ,')

        # load_5 text
        if len(parsed):
            cpu_5 = parsed.pop(0).strip(' ,')

        # load_15 text
        if len(parsed):
            cpu_15 = parsed.pop(0).strip(' ,')

        if cpu_15:
            self.logger.debug("CPU. up {0} users {1} cpu1 {2} cpu5 {3} cpu15 {4}".format(uptime, users, cpu_1, cpu_5, cpu_15))

            self.client.send("sensor/0/pigate/cpu/uptime", uptime, True)
            self.client.send("sensor/0/pigate/cpu/users", users, True)
            self.client.send("sensor/0/pigate/cpu/load_1m", cpu_1, True)
            self.client.send("sensor/0/pigate/cpu/load_5m", cpu_5, True)
            self.client.send("sensor/0/pigate/cpu/load_15m", cpu_15, True)
            self.client.send("sensor/0/pigate/cpu/timestamp", str(int(time.time())), True)
        else:
            self.logger.error("Skipped! '{0}'".format(data))
        # Send the raw data over mqtt
        #self.client.send("sensor-raw/0/cpu", data)

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
