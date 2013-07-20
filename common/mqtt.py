#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MQTT client initializer
"""

import mosquitto
import config
from error import MyHomeException
import common
import threading
import time

import re

__all__ = ["getMQTTClient", "MQTTClient"]


def getMQTTClient(client_id):

    conf = config.getConfig('mqtt')

    #clean = config.get("clean_session", True)

    client = mosquitto.Mosquitto(client_id)

    client.connect(conf.get("server"), conf.get("port"))

    return client


class MQTTClient():

    client_id = None

    connected = False
    connecting = False

    def __init__(self, client_id):
        self.subscriptions = []
        self.client_id = client_id

        self.client = mosquitto.Mosquitto(self.client_id)

        self.logger = common.get_logger("MQTT.{0}".format(client_id), True)

        self.logger.debug("Initialized")

    def connect(self):

        if self.connected or self.connecting:
            return

        self.logger.debug("Going to connect")

        self.connected = False
        self.connecting = True

        # Make sure there is a client id
        if not self.client_id:
            raise MQTTException("No client id set!")

        # connect
        conf = config.getConfig('mqtt')

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.on_publish = self.on_publish

        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe

        self.client.connect(conf.get("server"), int(conf.get("port")), 60)

        #clean = config.get("clean_session", True)
        self.logger.info("Connecting to: {0} : {1}".format(conf.get("server"), conf.get("port")))

        self.alive = True
        self.thread_looper = threading.Thread(target=self.looper)
        self.thread_looper.setDaemon(True)
        self.thread_looper.setName('mqtt_looper_{0}'.format(self.client_id))
        self.thread_looper.start()

    def disconnect(self):

        if self.connected:

            self.alive = False
            self.logger.info("Disconnecting")
            self.client.disconnect()

            for i in range(1000):
                if self.client.loop():
                    break

    def subscribe(self, topic, callback):

        self.logger.info("Subscribing to {0}".format(topic))

        # Convert topic into regex for matching messages
        regex = topic.replace("/#", "/.*")
        regex = regex.replace("/+/", "/[^/]+/")
        regex = regex.replace("/", "\/")
        #regex = "/" + regex + "/"

        regex = re.compile(regex)

        self.subscriptions.append({'r': regex, 't': topic, 'c': callback, 'e': False})

        self.do_subscribe()

    def unsubscribe(self, topic):

        self.logger.info("Unsubscribing from {0}".format(topic))

        self.client.unsubscribe(topic)

        # Find the related subscriptions
        for i in range(len(self.subscriptions)-1, -1, -1):

            sub = self.subscriptions[i]

            # Matching subscription? delete it
            if sub['t'] == topic:
                del self.subscriptions[i]

    def send(self, topic, message):

        self.logger.debug("Sending message {0} : '{1}'".format(topic, message))
        self.client.publish(topic, message, 0)

    def do_subscribe(self):

        if not self.connected:
            return

        self.logger.debug("Subscribing on mqtt")

        for sub in self.subscriptions:

            if not sub['e']:
                sub['e'] = True
                self.client.subscribe(sub['t'], 0)

                #print "Subscribe {0}".format(sub['t'])

    def looper(self):
        while self.alive:
            self.logger.debug("mqtt loop")
            time.sleep(0.50)
            self.loop()

    def loop(self):
        return self.client.loop()

    def on_connect(self, obj, rc):

        self.logger.info("Connected to the server. RC: {0}".format(rc))

        self.connecting = False
        #print "Connected"
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

    def on_disconnect(self, rc):

        self.logger.info("Disconnected. RC:{0}".format(rc))
        self.connected = False
        self.connecting = False
        self.alive = False

        if rc == 0:
            pass

        if rc == 1:
            self.logger.error("Unexpected disconnect")
            raise MQTTException("MQTT Unexpected disconnect")

    def on_message(self, obj, msg):
        #print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
        #
        for subscription in self.subscriptions:
            if subscription["r"].match(msg.topic):
                subscription["c"](msg)

    def on_publish(self, obj, mid):
        #print "Published " + str(mid)
        pass

    def on_subscribe(self, obj, mid, qos):
        self.logger.debug("Subscribed {0} {1}".format(mid, qos))
        #print "Subscribed "
        pass

    def on_unsubscribe(self, obj, mid):
        self.logger.debug("Unsubscribed {0}".format(mid))
        pass


class MQTTException(MyHomeException):
    pass
