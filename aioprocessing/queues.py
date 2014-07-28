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
    pass


class AioQueue(Queue, _AioQueueMixin):
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
    @asyncio.coroutine
    def coro_join(self):
        return (yield from self.execute(self.join))

