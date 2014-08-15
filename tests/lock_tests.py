import sys
import time
import asyncio
import unittest
import traceback
import aioprocessing
from multiprocessing import Process, Event, Queue, get_context

MANAGER_TYPE = 1
STANDARD_TYPE = 2

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
        self.type_ = STANDARD_TYPE
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

    def test_lock_cm(self):
        if self.type_ == MANAGER_TYPE:
            self.skipTest("Not relevant for manager type")
        event = Event()
        event2 = Event()
        @asyncio.coroutine
        def with_lock():
            with (yield from self.lock):
                event2.set()
                asyncio.sleep(1)
                event.wait()

        def sync_lock(lock, event2):
            event2.wait()
            self.assertEqual(self.lock.acquire(False), False)
            event.set()
            self.lock.acquire()
            self.lock.release()

        p = Process(target=sync_lock, args=(self.lock, event2))
        p.start()
        self.loop.run_until_complete(with_lock())
        p.join()

    def test_lock_consistency(self):
        if self.type_ == MANAGER_TYPE:
            self.skipTest("Not relevant for manager type")
        @asyncio.coroutine
        def do_lock():
            yield from self.lock.coro_release()

        def loop_run():
            self.loop.run_until_complete(do_lock())

        self.lock.acquire()
        self.assertRaises(RuntimeError, loop_run)

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


class LockManagerTest(LockTest):
    def setUp(self):
        super().setUp()
        self.type_ = MANAGER_TYPE
        self.manager = aioprocessing.Manager()
        self.lock = self.manager.AioLock()

class RLockTest(LockTest):
    def setUp(self):
        super().setUp()
        self.lock = aioprocessing.AioRLock()

class RLockManagerTest(LockTest):
    def setUp(self):
        super().setUp()
        self.type_ = MANAGER_TYPE
        self.manager = aioprocessing.Manager()
        self.lock = self.manager.AioRLock()

def mix_release(lock, q):
    try:
        try:
            lock.release()
        except (ValueError, AssertionError):
            pass
        else:
            q.put("Didn't get excepted AssertionError")
        lock.acquire()
        lock.release()
        q.put(True)
    except Exception as e:
        exc = traceback.format_exception(*sys.exc_info())
        q.put(exc)


class LockMixingTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.lock = aioprocessing.AioRLock()

    def test_mix_sync_to_async(self):
        self.lock.acquire()

        @asyncio.coroutine
        def do_release(choose_thread=False):
            yield from self.lock.coro_release(choose_thread=choose_thread)

        self.assertRaises(RuntimeError,
                          self.loop.run_until_complete, do_release())
        self.loop.run_until_complete(do_release(choose_thread=True))

    def test_mix_async_to_sync(self):
        @asyncio.coroutine
        def do_acquire():
            yield from self.lock.coro_acquire()

        self.loop.run_until_complete(do_acquire())
        self.assertRaises(RuntimeError, self.lock.release)
        self.lock.release(choose_thread=True)

    def test_mix_with_procs(self):
        @asyncio.coroutine
        def do_acquire():
            yield from self.lock.coro_acquire()
        @asyncio.coroutine
        def do_release(choose_thread=False):
            yield from self.lock.coro_release(choose_thread=choose_thread)
        q = Queue()
        p = Process(target=mix_release, args=(self.lock, q))
        self.loop.run_until_complete(do_acquire())
        p.start()
        self.loop.run_until_complete(do_release())
        out = q.get(timeout=5)
        p.join()
        self.assertTrue(isinstance(out, bool), out)

class SpawnLockMixingTest(LockMixingTest):
    def setUp(self):
        super().setUp()
        self.lock = aioprocessing.AioLock(context=get_context("spawn"))


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
        self.assertEqual(sem.release(choose_thread=True), None)
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

def set_event(event):
    event.set()

class EventTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.event = aioprocessing.AioEvent()

    def test_event(self):
        p = Process(target=set_event, args=(self.event,))

        @asyncio.coroutine
        def wait_event():
            yield from self.event.coro_wait()

        p.start()
        self.loop.run_until_complete(wait_event())
        p.join()

def cond_notify(cond, event):
    time.sleep(2)
    event.set()
    cond.acquire()
    cond.notify_all()
    cond.release()

class ConditionTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.cond = aioprocessing.AioCondition()

    def test_cond(self):
        event = Event()
        def pred():
            return event.is_set()

        @asyncio.coroutine
        def wait_for_pred():
            yield from self.cond.coro_acquire()
            yield from self.cond.coro_wait_for(pred)
            yield from self.cond.coro_release()

        p = Process(target=cond_notify, args=(self.cond, event))
        p.start()
        self.loop.run_until_complete(wait_for_pred())
        p.join()
