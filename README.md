aioprocessing
=============

A Python 3.3+ library that integrates the [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module with [asyncio](https://docs.python.org/3/library/asyncio.html).

Aioprocessing provides non-blocking coroutine versions of many blocking instance methods on objects in the `multiprocessing` library. Here's an example showing non-blocking usage of `Event`, `Queue`, and `Lock`:

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

How does it work?
-----------------

In most cases, this library makes blocking calls to `multiprocessing`
non-blocking by making the call in a `ThreadPoolExecutor`, and running that
executor using `asyncio.run_in_executor()`. It does *not* re-implement 
multiprocessing using asynchronous I/O. This means there is extra overhead
added when you use `aioprocessing` objects instead of `multiprocessing` objects,
because each one is generally introducing at least one `Threading.Thread` 
object, along with a `ThreadPoolExecutor`. It also means that all the normal
risks you get when you mix threads with fork apply here, too.

The one exception to this is `aioprocessing.AioPool`, which makes use of the 
existing `callback` and `error_callback` keyword arguments in the various 
`Pool.*_async` methods to run them as `asyncio` coroutines. Note that 
`multiprocessing.Pool` is actually using threads internally, so the thread/fork
mixing caveat still applies.

Note
----

This project is currently in alpha stages, and likely has bugs. Use at your own risk. (I do appreciate bug reports, though :).
