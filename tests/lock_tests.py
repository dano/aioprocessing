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
    def test_lock(self):
        lock = aioprocessing.AioLock()
        self.assertEqual(lock.acquire(), True)
        self.assertEqual(lock.acquire(False), False)
        self.assertEqual(lock.release(), None)

    def test_lock_async(self):
        lock = aioprocessing.AioLock()

        @asyncio.coroutine
        def do_async_lock():
            self.assertEqual((yield from lock.coro_acquire()), True)

        self.loop.run_until_complete(do_async_lock())

    def test_lock_multiproc(self):
        lock = aioprocessing.AioLock()
        e = Event()

        @asyncio.coroutine
        def do_async_lock():
            self.assertEqual((yield from lock.coro_acquire(False)), False)
            self.assertEqual((yield from lock.coro_acquire(timeout=4)), True)

        p = Process(target=do_lock_acquire, args=(lock, e))
        p.start()
        e.wait()
        self.loop.run_until_complete(do_async_lock())




