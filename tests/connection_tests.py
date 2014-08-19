import asyncio
import unittest
import aioprocessing
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

def conn_send(conn, val):
    conn.send(val)

class PipeTest(BaseTest):
    def test_pipe(self):
        conn1, conn2 = aioprocessing.AioPipe()
        val = 25
        p = Process(target=conn_send, args=(conn1, val))
        p.start()
        @asyncio.coroutine
        def conn_recv():
            out = yield from conn2.coro_recv()
            self.assertEqual(out, val)

        self.loop.run_until_complete(conn_recv())

if __name__ == "__main__":
    unittest.main()
