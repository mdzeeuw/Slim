import unittest
from drivers.serial import SerialGateway
import driver
from common.error import *


class TestSerialDriver(unittest.TestCase):

    def setUp(self):
        pass

    def test_initialize(self):

        d = SerialGateway()

    def test_setup(self):
        d = SerialGateway()

        self.assertIsInstance(d, driver.Driver)

        self.assertTrue(d.initialize())

        self.assertTrue(d.start())

        self.assertTrue(d.stop())

        self.assertTrue(d.restart())

        self.assertTrue(d.message("test"))


if __name__ == '__main__':
    unittest.main()
