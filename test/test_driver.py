import unittest
import driver
from common.error import *


class TestDriver(unittest.TestCase):

    def setUp(self):
        pass

    def test_initialize(self):

        d = driver.Driver()

    def test_unimplemented(self):
        d = driver.Driver()

        with self.assertRaises(MyHomeException):
            d.initialize()

        with self.assertRaises(MyHomeException):
            d.start()

        with self.assertRaises(MyHomeException):
            d.stop()

        with self.assertRaises(MyHomeException):
            d.restart()

        with self.assertRaises(MyHomeException):
            d.message("test")

    def test_mock(self):
        d = MockDriver()

        self.assertIsInstance(d, driver.Driver)

        self.assertTrue(d.initialize())

        self.assertTrue(d.start())

        self.assertTrue(d.stop())

        self.assertTrue(d.restart())

        self.assertTrue(d.message("test"))


class MockDriver(driver.Driver):
    """ Mock driver used for testing """

    def initialize(self):
        return True

    def start(self):
        return True

    def stop(self):
        return True

    def restart(self):
        return True

    def message(self, message):
        return True

if __name__ == '__main__':
    unittest.main()
