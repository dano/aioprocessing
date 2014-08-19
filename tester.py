#!/usr/bin/python3

import asyncio
from aioprocessing import AioManager
from concurrent.futures import ProcessPoolExecutor

@asyncio.coroutine
def _do_coro_proc_work(q, val, val2):
    ok = val + val2
    #yield from asyncio.sleep(4)
    print("Passing {} to parent".format(ok))
    yield from q.coro_put(ok)
    item = q.get()
    print("got {} back from parent".format(item))

def do_coro_proc_work(q, val, val2):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_do_coro_proc_work(q, val, val2))

@asyncio.coroutine
def do_work(q):
    print("hi")
    loop.run_in_executor(ProcessPoolExecutor(),
                         do_coro_proc_work, q, 1, 2)
    item = yield from q.coro_get()
    print("Got {} from worker".format(item))
    item = item + 25
    q.put(item)

if __name__  == "__main__":
    m = AioManager()
    q = m.AioQueue()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_work(q))
