import asyncio
import multiprocessing
from multiprocessing.queues import Queue, SimpleQueue, JoinableQueue

from .executor import _AioExecutorMixin

class _AioQueueMixin(_AioExecutorMixin):
    @asyncio.coroutine
    def coro_put(self, item):
        return (yield from self.execute(self.put, item))

    @asyncio.coroutine    
    def coro_get(self):
        return (yield from self.execute(self.get))

    #def __getattr__(self, name):
        #if (not name.startswith("__") and
            #hasattr(self._queue, name)):
            #return getattr(self._queue, name)
        #else:
            #raise AttributeError("'%s' object has no attribute '%s'" % 
                                    #(self.__class__.__name__, name))

class AioSimpleQueue(SimpleQueue, _AioQueueMixin):
    """ An asyncio-friendly version of mp.SimpleQueue. 
    
    Provides two asyncio.coroutines: coro_get and coro_put,
    which are asynchronous version of get and put, respectively.
    
    """
    pass


class AioQueue(Queue, _AioQueueMixin):
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

class AioJoinableQueue(JoinableQueue, _AioQueueMixin):
    """ An asyncio-friendly version of mp.JoinableQueue. 
    
    Provides three asyncio.coroutines: coro_get, coro_put, and
    coro_join, which are asynchronous version of get put, and
    join, respectively.
    
    """
    @asyncio.coroutine
    def coro_join(self):
        return (yield from self.execute(self.join))

