import time
import asyncio
import unittest
import aioprocessing
from multiprocessing import Process, Event

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

def do_lock_acquire(lock, e):
    lock.acquire()
    e.set()
    time.sleep(2)
    lock.release()

class LockTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.lock = aioprocessing.AioLock()

    def test_lock(self):
        self.lock = aioprocessing.AioLock()
        self.assertEqual(self.lock.acquire(), True)
        self.assertEqual(self.lock.acquire(False), False)
        self.assertEqual(self.lock.release(), None)

    def test_lock_async(self):
        @asyncio.coroutine
        def do_async_lock():
            self.assertEqual((yield from self.lock.coro_acquire()), True)

        self.loop.run_until_complete(do_async_lock())

    def test_lock_multiproc(self):
        e = Event()

        @asyncio.coroutine
        def do_async_lock():
            self.assertEqual((yield from self.lock.coro_acquire(False)), 
                             False)
            self.assertEqual((yield from self.lock.coro_acquire(timeout=4)), 
                             True)

        p = Process(target=do_lock_acquire, args=(self.lock, e))
        p.start()
        e.wait()
        self.loop.run_until_complete(do_async_lock())



class RLockTest(LockTest):
    def setUp(self):
        super().setUp()
        self.lock = aioprocessing.AioRLock()

