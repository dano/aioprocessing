import asyncio
import unittest
import aioprocessing
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

def queue_put(q, val):
    val = q.put(val)
    return val

def queue_get(q):
    val = q.get()
    q.put(val)


class QueueTest(BaseTest):
    def test_blocking_put(self):
        q = aioprocessing.AioQueue()

        @asyncio.coroutine
        def queue_put():
            yield from q.coro_put(1)

        self.loop.run_until_complete(queue_put())

    def test_put_get(self):
        q = aioprocessing.AioQueue()
        val = 1
        p = Process(target=queue_put, args=(q, val))

        @asyncio.coroutine
        def queue_get():
            ret = yield from q.coro_get()
            self.assertEqual(ret, val)

        p.start()
        self.loop.run_until_complete(queue_get())
        p.join()

    def test_get_put(self):
        q = aioprocessing.AioQueue()
        val = 2

        @asyncio.coroutine
        def queue_put():
            yield from q.coro_put(val)

        p = Process(target=queue_get, args=(q,))
        p.start()
        self.loop.run_until_complete(queue_put())
        p.join()
        out = q.get()
        self.assertEqual(out, val)

    def test_simple_queue(self):
        q = aioprocessing.AioSimpleQueue()
        val = 8
        @asyncio.coroutine
        def queue_put():
            yield from q.coro_put(val)

        self.loop.run_until_complete(queue_put())
        out = q.get()
        self.assertEqual(val, out)


class ManagerQueueTest(BaseTest):
    def test_executor(self):
        m = aioprocessing.Manager()
        q = m.AioQueue()
        p = ProcessPoolExecutor(max_workers=1)
        val = 4
        yield p.submit(queue_put, q, val)

        @asyncio.coroutine
        def queue_get():
            out = yield from q.coro_get()
            self.assertEqual(out, val)
        self.loop.run_until_complete(queue_get())
        p.shutdown()


class JoinableQueueTest(BaseTest):
    def test_join_empty_queue(self):
        q = aioprocessing.AioJoinableQueue()

        @asyncio.coroutine
        def join():
            yield from q.coro_join()

        self.loop.run_until_complete(join())


if __name__ == "__main__":
    unittest.main()
