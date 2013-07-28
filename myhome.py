#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Myhome Core file
"""
import common.common


class MyHome():
    pass


class Monitor():
    """
        Class responsible for monitoring of the processes / drivers
    """
    pass


class Loader():
    """
        Class responsible for loading / unloading drivers
    """
    pass

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', help='Driver to load')
    parser.add_argument('-a', help='Action')
    parser.add_argument('-d', help='Debug')
    args = parser.parse_args()

    driver = None

    if args.d:
        debug = True
    else:
        debug = False

    # Regular logger
    if debug:
        logger = common.common.get_logger("MyHome Manager", True)
    else:
        logger = common.common.get_file_logger("MyHome Manager", False)

    if args.m == "serial":
        from drivers.serialgateway import SerialGateway
        driver = SerialGateway()

    elif args.m == "cpumon":
        from drivers.cpumonitor import CPUMonitor
        driver = CPUMonitor()

    elif args.m == "sensor":
        from drivers.sensordecoder import SensorDecoder
        driver = SensorDecoder()

    elif args.m == "monitor":
        from drivers.systemmonitor import SystemMonitor
        driver = SystemMonitor()

    elif args.m == "outside":
        from drivers.outsidemonitor import OutsideMonitor
        driver = OutsideMonitor()

    name = driver.__class__.__name__.lower()

    if driver:

        if args.a == "start":

            logger.info("Starting {0}".format(name))

            try:
                driver.initialize(debug)

                driver.start()
            except Exception as e:
                logger.error("Error in {0}".format(name))
                logger.error(e)
                raise
            finally:
                logger.info("Quit {0}".format(name))

        elif args.a == "stop":

            import common.mqtt
            import time

            logger.info("Killing {0}".format(name))

            # Send mqtt message to stop
            client = common.mqtt.MQTTClient("MyHomeLauncer")
            client.connect()

            for i in range(50):
                if client.connected:
                    break

                time.sleep(0.01)

            client.send("command/{0}".format(name), "stop", 0, 0, True)

            client.disconnect()

            for i in range(50):
                if not client.connected:
                    break

                time.sleep(0.1)

        else:
            print "No action given"

    else:
        print "No driver specified"
