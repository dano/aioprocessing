from multiprocessing import Pool
from asyncio import Future
import asyncio

from .executor import CoroBuilder

__all__ = ['AioPool']

class AioPool(metaclass=CoroBuilder):
    delegate = Pool
    coroutines = ['join']

    def coro_func(self, funcname, *args, **kwargs):
        loop = asyncio.get_event_loop()
        fut = Future()
        def set_result(result):
            loop.call_soon_threadsafe(fut.set_result, result)
        def set_exc(exc):
            loop.call_soon_threadsafe(fut.set_exception, exc)

        func = getattr(self._obj, funcname)
        func(*args, callback=set_result, 
             error_callback=set_exc, **kwargs)
        return fut

    def coro_apply(self, func, args=(), kwds={}):
        return self.coro_func('apply_async', func, 
                              args=args, kwds=kwds)

    def coro_map(self, func, iterable, chunksize=None):
        return self.coro_func('map_async', func, iterable, 
                              chunksize=chunksize)

    def coro_starmap(self, func, iterable, chunksize=None):
        return self.coro_func('starmap_async', func, iterable, 
                              chunksize=chunksize)
