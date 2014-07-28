import asyncio
from queue import Queue
from multiprocessing.managers import SyncManager, BaseProxy, MakeProxyType

from . import queues

__all__ = ['Manager']

AioBaseQueueProxy = MakeProxyType('AioQueueProxy', (
    'task_done', 'get', 'qsize', 'put', 'put_nowait', 
    'get_nowait', 'empty', 'join', '_qsize', 'full'
    ))
     
class AioQueueProxy(queues._AioQueueMixin, AioBaseQueueProxy):
    @asyncio.coroutine
    def coro_get(self):
        return (yield from self.execute(self._callmethod, 'get'))

    @asyncio.coroutine
    def coro_put(self, item):
        return (yield from self.execute(self._callmethod, 'put', (item,)))


class AioManager(SyncManager):
    pass
AioManager.register("AioQueue", Queue, AioQueueProxy)


def Manager():
    m = AioManager()
    m.start()
    return m

