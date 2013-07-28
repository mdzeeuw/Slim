#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import common.config
import driver
import httplib
import urllib
import zlib

import time
import logging
from datetime import date


class OutsideMonitor(driver.Driver):

    NAME = "OutsideMonitor"

    last_check_time = None

    def load(self):
        self.config = common.config.Config("outside")

        self.CHECK_INTERVAL = int(self.config.get('interval', 120))

        if not self.CHECK_INTERVAL:
            raise Exception("Invalid interval in config")

        self.topic = self.config.get('topic')

        if not self.topic:
            raise Exception("Invalid topic in config")

        self.data_items = self.config.get('clientraw')['data']
        self.custom_items = self.config.get('clientraw')['custom']

        self.data_logger = MyhomeOnlineLogger()

    def run(self):

        if self.last_check_time is None or time.time() - self.last_check_time > self.CHECK_INTERVAL:
            self.handleData(self.getData())

            self.last_check_time = time.time()

    def getData(self):
        data = None

        try:
            conn = httplib.HTTPConnection(self.config.get('host'))
            #conn.set_debuglevel(4)
            conn.request("GET", self.config.get('file'), None, self.config.get('headers'))
            response = conn.getresponse()
            #print response.getheaders()
            #print response.status, response.reason

            raw = response.read()

            if response.getheader('content-encoding') == 'gzip':
                self.logger.debug("Got gzip response")
                data = zlib.decompress(raw, 16+zlib.MAX_WBITS)
                #print decompressed_data
            else:
                self.logger.error("Unknown encoding: {0}".format(response.getheaders()))

        except Exception as e:
            self.logger.error(e)

        try:
            if conn:
                conn.close()
        except:
            pass

        return data

    def handleData(self, raw_data):

        if not raw_data:
            self.logger.info("No data from source")
            return
        else:
            self.logger.debug("Got data".format(raw_data))

        # Log the data
        self.data_logger.write(raw_data)

        # Split the fields
        data = raw_data.split(' ')

        # Should have correct amount of fields
        if len(data) >= len(self.data_items):

            self.logger.debug("Parsing data {0} : {1}".format(len(data), len(self.data_items)))

            for data_item in self.data_items:

                data_item['value'] = data.pop(0)

                if 'publish' in data_item and data_item['publish']:
                    self.client.send(self.topic.format(data_item['publish']), data_item['value'])

                if 'merge' in data_item:
                    if 'index' in data_item['merge'] and 'variable' in data_item['merge']:
                        i = data_item['merge']['index']
                        v = data_item['merge']['variable']

                        if v not in self.custom_items:
                            raise Exception("Not found custom" + v)
                            continue

                        self.custom_items[v]['data'][int(i)] = data_item['value']

            self.client.send(self.topic.format('timestamp'), str(int(time.time())), True)

            for item in self.custom_items:
                custom_item = self.custom_items[item]
                if not 'publish' in custom_item:
                    continue

                t = custom_item['format'] % tuple(custom_item['data'])

                self.client.send(self.topic.format(custom_item['publish']), t)

        self.logger.debug("Send data")

    def restart(self):
        self.logger.info("Restarting")
        return True

    def message(self, message):
        return True


class MyhomeOnlineLogger:
    def __init__(self):
        self.handler = False
        self.logger = False
        self.today = False

    def write(self, data):

        #Create a new log each day
        self.check_log()

        #toHex = lambda data:"".join([hex(ord(c))[2:].zfill(2) for c in data])
        #data_hex = data.encode("hex")

        self.logger.info(data)

    def check_log(self):
        if not self.logger:
            self.open_data_log()
            return

        #new day new logger
        if self.today != date.today():
            self.open_data_log()

        return

    def open_data_log(self):

        os.environ['TZ'] = 'Europe/Amsterdam'
        time.tzset()

        # Logger initialization
        #Name could be read from actual device
        app_logger = logging.getLogger("online")
        app_logger.setLevel(logging.INFO)

        if self.handler:
            try:
                app_logger.removeHandler(self.handler)
            except Exception, e:
                pass

            self.handler = False

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")

        self.today = date.today()
        try:
            folder = "logs/%d-%02d" % (self.today.year, self.today.month)

            if not os.path.exists(folder):
                os.makedirs(folder)

            self.handler = logging.FileHandler("%s/online-%s.log" % (folder, self.today))
            self.handler.setFormatter(formatter)

            app_logger.addHandler(self.handler)
        except:
            return False

        self.logger = app_logger
