import unittest

import mosquitto

mqtt_client_id = "UnitTestClient"


class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def test_config(self):

        import common.config

        config = common.config.Config('test')

        self.assertIsInstance(config, common.config.Config)

        self.assertEqual(config.data['test2'], "Hi world")
        self.assertEqual(config.get('test2'), "Hi world")

        self.assertEqual(config.get('doesnotexist'), None)
        self.assertEqual(config.get('doesnotexist2', False), False)

    def test_mqtt(self):

        import common.mqtt

        client = common.mqtt.getMQTTClient(mqtt_client_id)

        self.assertIsInstance(client, mosquitto.Mosquitto)

        clientObj = common.mqtt.MQTTClient(mqtt_client_id)

        self.assertIsInstance(clientObj, common.mqtt.MQTTClient)

        def callback1(message):

            self.assertEqual(topic, "unittest/1/test/test1")

        def callback2(message):

            self.assertEqual(topic, "unittest/2/test/test1")

        def callback3(message):

            self.assertEqual(topic, "unittest/3/test/test1")

            clientObj.disconnect()

        clientObj.subscribe('unittest/+/test/#', callback1)
        clientObj.subscribe('unittest/2/#', callback2)
        clientObj.subscribe('unittest/3/test3', callback3)

#        clientObj.connect()


if __name__ == '__main__':
    unittest.main()
