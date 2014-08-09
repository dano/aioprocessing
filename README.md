aioprocessing
=============

A Python 3.4+ library that integrates the [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module with [asyncio](https://docs.python.org/3/library/asyncio.html).

Aioprocessing provides non-blocking coroutine versions of many blocking instance methods on objects in the `multiprocessing` library. Here's an example showing non-blocking usage of `Event`, `Queue`, and `Lock`.

```python
import time
import asyncio
import aioprocessing
import multiprocessing


def func(queue, event, lock, items):
    """ Demo worker function.

    This worker function runs in its own process, and uses
    normal blocking calls to aioprocessing objects.

    """
    with lock:
        event.set()
        for item in items:
            time.sleep(3)
            queue.put(item+5)
    queue.close()

@asyncio.coroutine
def example(queue, event, lock):
    print("starting")
    l = [1,2,3,4,5]
    p = multiprocessing.Process(target=func, args=(queue, event, lock, l))
    p.start()
    while True:
        result = yield from queue.coro_get() # Non-blocking
        if result is None:
            break
        print("Got result {}".format(result))
    p.join()

@asyncio.coroutine
def example2(queue, event, lock):
    yield from event.coro_wait()  # Non-blocking
    with (yield from lock):  # Non-blocking
        yield from queue.coro_put(78)
        yield from queue.coro_put(None) # Shut it down

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    queue = aioprocessing.AioQueue()
    lock = aioprocessing.AioLock()
    event = aioprocessing.AioEvent()
    tasks = [
        asyncio.async(example(queue, event, lock)), 
        asyncio.async(example2(queue, event, lock)),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
```
