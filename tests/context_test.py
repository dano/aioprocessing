import unittest
from aioprocessing import get_context
from multiprocessing.context import ForkContext


class PickleTest(unittest.TestCase):
    def test_get_context(self):
        ctx = get_context("fork")
        self.assertIsInstance(ctx, ForkContext)
