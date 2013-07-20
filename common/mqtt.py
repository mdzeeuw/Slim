#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MQTT client initializer
"""

import mosquitto
import common.config
from common.error import MyHomeException

import re

__all__ = ["getMQTTClient", "MQTTClient"]


def getMQTTClient(client_id):

    config = common.config.getConfig('mqtt')

    #clean = config.get("clean_session", True)

    client = mosquitto.Mosquitto(client_id)

    client.connect(config.get("server"), config.get("port"))

    return client


class MQTTClient():

    client_id = None

    connected = False
    connecting = False

    def __init__(self, client_id):
        self.subscriptions = []
        self.client_id = client_id

        self.client = mosquitto.Mosquitto(self.client_id)

    def connect(self):

        if self.connected or self.connecting:
            return

        print "Connecting " + self.client_id

        self.connected = False
        self.connecting = True

        # Make sure there is a client id
        if not self.client_id:
            raise MQTTException("No client id set!")

        # connect
        config = common.config.getConfig('mqtt')

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.on_publish = self.on_publish

        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe

        self.client.connect(config.get("server"), int(config.get("port")), 60)
        #clean = config.get("clean_session", True)
        #print "Connecting to: {0} : {1}".format(config.get("server"), config.get("port"))

    def disconnect(self):
        if self.connected:
            self.client.disconnect()

    def subscribe(self, topic, callback):

        # Convert topic into regex for matching messages
        regex = topic.replace("/#", "/.*")
        regex = regex.replace("/+/", "/[^/]+/")
        regex = regex.replace("/", "\/")
        #regex = "/" + regex + "/"

        regex = re.compile(regex)

        self.subscriptions.append({'r': regex, 't': topic, 'c': callback, 'e': False})

        self.do_subscribe()

    def unsubscribe(self, topic):

        self.client.unsubscribe(topic)

        for i in range(len(self.subscriptions)-1, -1, -1):

            sub = self.subscriptions[i]
            if sub['t'] == topic:
                #print "Del sub "
                #print sub
                del self.subscriptions[i]

    def send(self, topic, message):
        self.client.publish(topic, message, 0)

    def do_subscribe(self):

        if not self.connected:
            return

        for sub in self.subscriptions:

            if not sub['e']:
                sub['e'] = True
                self.client.subscribe(sub['t'], 0)

                print "Subscribe {0}".format(sub['t'])

    def loop(self):
        return self.client.loop()

    def on_connect(self, obj, rc):

        self.connecting = False
        print "Connected"
        # OK
        if rc == 0:
            self.connected = True
            self.send("unittest/test", "Connected OK")
            self.do_subscribe()

        # Protocol version not accepted
        if rc == 1:
            raise MQTTException("MQTT protocol not accepted")

        # Identifier rejected
        if rc == 2:
            raise MQTTException("MQTT Identifier rejected")

        # Server unavailable
        if rc == 3:
            raise MQTTException("MQTT server unavailable")

        # Bad user name or password
        if rc == 4:
            raise MQTTException("MQTT bad user name or password")

        # Not authorised
        if rc == 5:
            raise MQTTException("MQTT not authorised")

    def on_disconnect(self, obj, rc):

        print "Disconnected"
        self.connected = False
        self.connecting = False

        if rc == 0:
            pass

        if rc == 1:
            raise MQTTException("MQTT Unexpected disconnect")

    def on_message(self, obj, msg):
        print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
        #
        for subscription in self.subscriptions:
            if subscription["r"].match(msg.topic):
                subscription["c"](msg)

    def on_publish(self, obj, mid):
        print "Published " + str(mid)

    def on_subscribe(self, obj, mid, qos):
        print "Subscribed "

    def on_unsubscribe(self, obj, mid):
        print "UnSubscribed " + str(mid)


class MQTTException(MyHomeException):
    pass
