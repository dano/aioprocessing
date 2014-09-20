import asyncio
import unittest
import aioprocessing
from multiprocessing import Event
import time

from ._base_test import BaseTest, _GenMixin

def work_func(a, b):
    c = a * b
    return c

def map_func(z):
    return z * 3

def starmap(func, it):
    return map(func, *zip(*it))

class GenAioPoolTest(BaseTest, _GenMixin):
    def setUp(self):
        super().setUp()
        self.Obj = aioprocessing.AioPool
        self.inst = self.Obj(1)
        self.initargs = (1,)
        self.meth = 'coro_map'
        self.args = (map_func, [1,2,3],)

class PoolTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.pool = aioprocessing.AioPool()

    def tearDown(self):
        super().tearDown()
        self.pool.close()
        self.pool.join()

    def test_ctx_mgr(self):
        with aioprocessing.AioPool() as pool:
            self.assertIsInstance(pool, aioprocessing.pool.AioPool)
        self.assertRaises(ValueError, pool.map, map_func, [1])

    def test_coro_apply(self):
        @asyncio.coroutine
        def do_apply():
            out = yield from self.pool.coro_apply(work_func, args=(2, 3))
            self.assertEqual(out, 6)

        self.loop.run_until_complete(do_apply())

    def test_coro_map(self):
        it = list(range(5))
        @asyncio.coroutine
        def do_map():
            out = yield from self.pool.coro_map(map_func, it)
            self.assertEqual(out, list(map(map_func, it)))

        self.loop.run_until_complete(do_map())

    def test_coro_starmap(self):
        it = list(zip(range(5), range(5,10)))
        @asyncio.coroutine
        def do_starmap():
            out = yield from self.pool.coro_starmap(work_func, it)
            self.assertEqual(out, list(starmap(work_func, it)))

        self.loop.run_until_complete(do_starmap())

    def test_coro_join(self):
        @asyncio.coroutine
        def do_join():
            yield from self.pool.coro_join()

        self.pool.close()
        self.loop.run_until_complete(do_join())

