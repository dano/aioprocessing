import asyncio
import multiprocessing
from multiprocessing.queues import Queue, SimpleQueue, JoinableQueue

from .executor import _AioExecutorMixin, CoroBuilder


class AioBaseQueue(_AioExecutorMixin, metaclass=CoroBuilder):
    coroutines = ['get', 'put']


class AioSimpleQueue(AioBaseQueue, SimpleQueue):
    """ An asyncio-friendly version of mp.SimpleQueue. 
    
    Provides two asyncio.coroutines: coro_get and coro_put,
    which are asynchronous version of get and put, respectively.
    
    """
    pass


class AioQueue(AioBaseQueue, Queue):
    """ An asyncio-friendly version of mp.SimpleQueue. 
    
    Provides two asyncio.coroutines: coro_get and coro_put,
    which are asynchronous version of get and put, respectively.
    
    """
    def __init__(self, maxsize=0, *, ctx):
        super().__init__(maxsize, ctx=ctx)
        self._cancelled_join = False

    def cancel_join_thread(self):
        self._cancelled_join = True
        super().cancel_join_thread()

    def join_thread(self):
        super().join_thread()
        if self._executor and not self._cancelled_join:
            self._executor.shutdown()


class AioJoinableQueue(AioBaseQueue, JoinableQueue, metaclass=CoroBuilder):
    """ An asyncio-friendly version of mp.JoinableQueue. 
    
    Provides three asyncio.coroutines: coro_get, coro_put, and
    coro_join, which are asynchronous version of get put, and
    join, respectively.
    
    """
    coroutines = ['join']

