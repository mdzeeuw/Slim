import unittest
import myhome


class TestMyHomeCore(unittest.TestCase):

    def setUp(self):
        pass

    def test_initialize(self):

        core = myhome.MyHome()

        watcher = myhome.Monitor()

        loader = myhome.Loader()

if __name__ == '__main__':
    unittest.main()
