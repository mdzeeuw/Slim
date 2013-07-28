import sys
import driver
import common.config
import common.error
import common.common
import common.mqtt
import serial

import time
import threading

import os
import logging
from datetime import date


class SerialGateway(driver.Driver):

    NAME = "SerialGateway"

    def start(self):
        # Get my config
        self.config = common.config.Config("serial")

        self.data_logger = MyhomeDataLogger()

        # Set alive flag
        self.alive = True

        # Start reading thread
        self.thread_read = threading.Thread(target=self.serial_worker)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial_worker')
        self.thread_read.start()

        super(SerialGateway, self).start()

        # Run for close to ever
    def run(self):

        pass

    def serial_worker(self):

        # Get settings
        port = self.config.get("port", "/dev/ttyAMA0")
        speed = self.config.get("speed", 9600)

        self.logger.info("Setup serial connection {0} {1}".format(port, speed))

        try:
            # Make connection
            serial_conn = serial.Serial(port, speed)

            # Clear the current buffers
            serial_conn.flushInput()
            serial_conn.flushOutput()

            while self.running:
                # get the raw data, clean the line breaks
                self.logger.debug("Serial reading line")
                ser_data = serial_conn.readline().strip(' \t\n\r')
                self.logger.debug("Serial data received")
                # Append the group
                ser_data = "44 " + ser_data

                #self._write_lock.acquire()
                #try:
                self.handleData(ser_data)
                #finally:
                #    pass
                #self._write_lock.release()

                time.sleep(0.001)

            # The end
            self.logger.info("Closing serial connection")
            try:
                serial_conn.close()
            finally:
                pass

        except:
            self.logger.error("Error in serial worker")
            raise
        finally:
            self.alive = False
            self.logger.info("Serial worker stopped")

    def handleData(self, data):

        self.logger.debug("Got data {0}".format(data))

        # Write the raw data to disk
        self.data_logger.write(data)

        # Split into the bytes
        parsed = data.split(" ")

        # At least node, header
        if len(parsed) > 2:
            group = parsed[0]
            node = parsed[1]

            self.logger.debug("Sending to sensor-raw/{0}/{1}".format(group, node))

            # Send the raw data over mqtt
            self.client.send("sensor-raw/{0}/{1}".format(group, node), data)

    def stop(self):

        super(SerialGateway, self).stop()

        # Wait for the serial thread to finish
        self.thread_read.join()

        return True

    def restart(self):
        self.logger.info("Restarting")
        return True

    def message(self, message):
        return True


class MyhomeDataLogger:
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
        app_logger = logging.getLogger("serial")
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

            self.handler = logging.FileHandler("%s/%s.log" % (folder, self.today))
            self.handler.setFormatter(formatter)

            app_logger.addHandler(self.handler)
        except Exception, e:
            return False

        self.logger = app_logger


if __name__ == '__main__':
    gw = SerialGateway()

    gw.start()
