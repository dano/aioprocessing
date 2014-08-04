import time
import asyncio
import unittest
import aioprocessing
from multiprocessing import Process, Event

def get_value(self):
    try:
        return self.get_value()
    except AttributeError:
        try:
            return self._Semaphore__value
        except AttributeError:
            try:
                return self._value
            except AttributeError:
                raise NotImplementedError

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

class SemaphoreTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.sem = aioprocessing.AioSemaphore(2)

    def _test_semaphore(self, sem):
        self.assertReturnsIfImplemented(2, get_value, sem)
        self.assertEqual(sem.acquire(), True)
        self.assertReturnsIfImplemented(1, get_value, sem)

        @asyncio.coroutine
        def sem_acquire():
            self.assertEqual((yield from sem.coro_acquire()), True)
        self.loop.run_until_complete(sem_acquire())
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.acquire(False), False)
        self.assertReturnsIfImplemented(0, get_value, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(1, get_value, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(2, get_value, sem)

    def test_semaphore(self):
        sem = self.sem
        self._test_semaphore(sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(3, get_value, sem)
        self.assertEqual(sem.release(), None)
        self.assertReturnsIfImplemented(4, get_value, sem)

class BoundedSemaphoreTest(SemaphoreTest):
    def setUp(self):
        super().setUp()
        self.sem = aioprocessing.AioBoundedSemaphore(2)

    def test_semaphore(self):
        self._test_semaphore(self.sem)

def barrier_wait(barrier, event):
    event.set()
    barrier.wait()

class BarrierTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.barrier = aioprocessing.AioBarrier(2)

    def _wait_barrier(self):
        self.barrier.wait()

    def test_barrier(self):
        event = Event()
        @asyncio.coroutine
        def wait_barrier_async():
            yield from self.barrier.coro_wait()

        def wait_barrier():
            fut = asyncio.async(wait_barrier_async())
            yield from asyncio.sleep(.5)
            self.assertEqual(self.barrier.n_waiting, 1)
            self.barrier.wait()

        #t = threading.Thread(target=self._wait_barrier)
        #t.start()
        self.loop.run_until_complete(wait_barrier())

    def test_barrier_multiproc(self):
        event = Event()
        p = Process(target=barrier_wait, args=(self.barrier, event))
        p.start()
        @asyncio.coroutine
        def wait_barrier():
            event.wait()
            yield from asyncio.sleep(.2)
            self.assertEqual(self.barrier.n_waiting, 1)
            yield from self.barrier.coro_wait()
        self.loop.run_until_complete(wait_barrier())
        p.join()
