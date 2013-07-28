#!/usr/bin/env python
# -*- coding: utf-8 -*-

import driver

import subprocess
import time
import re
import json


class SystemMonitor(driver.Driver):

    CHECK_INTERVAL = 60
    NAME = "SystemMonitor"

    last_check_time = None

    def run(self):

        if self.last_check_time is None or time.time() - self.last_check_time > self.CHECK_INTERVAL:
            self.handleProcs(self.getProcesses())

            self.handleData(self.getMemory())
            self.last_check_time = time.time()

    def handleProcs(self, data):

        self.logger.debug("Got data".format(data))

        parsed = data.split("\n")

        regex = re.compile('([0-9]+)\s*([^\s0-9][^\s]*)\s*([^\s]*)[\s\\\_\|]*([0-9]+\:[0-9]{2})\s*(.*)')

        regex2 = re.compile('python myhome')
        data = {}
        for d in parsed:

            m = regex.match(d.strip(' \t\n\r'))
            if m:
                proc = m.group(5).strip(' \\|_')

                if regex2.match(proc):
                    data[m.group(1)] = {'process': proc, 'cputime': m.group(4)}

        self.client.send("sensor/0/pigate/processes", json.dumps(data))

        #print parsed

    def handleData(self, data):

        self.logger.debug("Got data".format(data))

        parsed = data.split("\n")

        data = {}

        # Extract the usefull bits
        keep = ["memtotal", "memfree", "cached", "swaptotal", "swapfree", "swapcached"]

        for i in parsed:
            d = i.split(':')

            if len(d) != 2:
                continue

            # send this
            if d[0].lower() in keep:
                #data[d[0].lower()] = d[1].strip(' \t\n\r')

                self.client.send("sensor/0/pigate/mem/{0}".format(d[0].lower()), d[1].strip(' \t\n\r'))

        self.client.send("sensor/0/pigate/mem/timestamp", str(int(time.time())), True)

        self.logger.debug("Send data")

    def restart(self):
        self.logger.info("Restarting")
        return True

    def message(self, message):
        return True

    def getMemory(colName):
        """Get a column of ps output as a list"""
        ps = subprocess.Popen(["cat", "/proc/meminfo"], stdout=subprocess.PIPE)
        (stdout, stderr) = ps.communicate()
        data = stdout.strip()
        return data

    def getProcesses(colName):
        """Get a column of ps output as a list"""
        ps = subprocess.Popen(["ps", "axf"], stdout=subprocess.PIPE)
        (stdout, stderr) = ps.communicate()
        data = stdout.strip()
        return data
