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
    disconnecting = False

    def __init__(self, client_id, debug=False):
        self.subscriptions = []
        self.client_id = client_id

        self.client = mosquitto.Mosquitto(self.client_id)

        # Regular logger
        if debug:
            self.logger = common.get_logger("MQTT.{0}".format(client_id), True)
        else:
            self.logger = common.get_file_logger("MQTT.{0}".format(client_id), False)

        self.lock = threading.RLock()

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

        self.client.connect(conf.get("server"), int(conf.get("port")), 120)

        #clean = config.get("clean_session", True)
        self.logger.info("Connecting to: {0} : {1}".format(conf.get("server"), conf.get("port")))

        self.thread_looper = threading.Thread(target=self.looper)
        self.thread_looper.setDaemon(True)
        self.thread_looper.setName('mqtt_looper_{0}'.format(self.client_id))
        self.thread_looper.start()

        # Wait for the connection
        for i in range(50):
            time.sleep(0.1)
            if self.connected:
                break

        time.sleep(0.1)
        return self.connected

    def disconnect(self):

        if self.connected and not self.disconnecting:

            self.disconnecting = True

            self.alive = False
            self.logger.info("Disconnecting")
            with self.lock:
                self.client.disconnect()

            for i in range(1000):
                if self.client.loop():
                    break

            self.logger.info("Succesfull disconnect")

    def kill(self):
        self.alive = False
        try:
            self.client.disconnect()

            for i in range(1000):
                if self.client.loop():
                    break
                time.sleep(0.01)

        finally:
            pass

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

        with self.lock:
            self.client.unsubscribe(topic)

        # Find the related subscriptions
        for i in range(len(self.subscriptions)-1, -1, -1):

            sub = self.subscriptions[i]

            # Matching subscription? delete it
            if sub['t'] == topic:
                del self.subscriptions[i]

    def send(self, topic, message, retain=0, qos=0):
        if retain:
            retain = 1

        with self.lock:
            self.logger.debug("Sending message {0} : '{1}' q{2} r{3}".format(topic, message, qos, retain))
            self.client.publish(topic, message, qos, True)

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
        self.alive = True
        self.logger.info("Looper started")
        while self.alive:
            try:
                time.sleep(0.001)
                with self.lock:
                    self.loop()

            except Exception as e:
                self.logger.error(e)
                raise

        self.alive = False
        self.logger.info("Looper stopped")

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

    def on_disconnect(self, obj):

        rc = 0
        self.logger.info("Disconnected. RC:{0}".format(rc))
        self.connected = False
        self.connecting = False
        self.alive = False
        self.disconnecting = False

        if rc == 0:
            pass

        elif rc == 1:
            self.logger.error("Unexpected disconnect")
            #raise MQTTException("MQTT Unexpected disconnect")

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
