import asyncio
import unittest

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def assertReturnsIfImplemented(self, value, func, *args):
        try:
            res = func(*args)
        except NotImplementedError:
            pass
        else:
            return self.assertEqual(value, res)
