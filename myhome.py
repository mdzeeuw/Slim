#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Myhome Core file
"""
from drivers.serialgateway import SerialGateway
from drivers.cpumonitor import CPUMonitor


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
    #d = SerialGateway()
    d = CPUMonitor()

    d.initialize()

    d.start()
