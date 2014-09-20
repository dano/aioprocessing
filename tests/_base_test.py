import asyncio
import unittest
import multiprocessing

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


class _GenMixin:
    initargs = ()
    args = ()

    def test_loop(self):
        loop = asyncio.new_event_loop()
        getattr(self.inst, self.meth)(*self.args, loop=loop)
        self._after()

    def test_ctx(self):
        ctx = multiprocessing.get_context("spawn")
        self.Obj(*self.initargs, context=ctx)

    def _after(self):
        pass
