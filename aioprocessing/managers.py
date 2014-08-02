import asyncio
from queue import Queue
from threading import (Barrier, BoundedSemaphore, Condition, Event,
                       Lock, RLock, Semaphore)
from multiprocessing.managers import (SyncManager, BaseProxy, MakeProxyType,
                                      BarrierProxy, EventProxy, ConditionProxy,
                                      AcquirerProxy)

from . import queues
from .executor import _AioExecutorMixin

__all__ = ['Manager']

AioBaseQueueProxy = MakeProxyType('AioQueueProxy', (
    'task_done', 'get', 'qsize', 'put', 'put_nowait', 
    'get_nowait', 'empty', 'join', '_qsize', 'full'
    ))

class _AioProxyMixin(_AioExecutorMixin):
    @asyncio.coroutine
    def _async_call(self, method, args=()):
        return (yield from self.execute(self._callmethod, method, args))


class AioQueueProxy(_AioProxyMixin, AioBaseQueueProxy):
    """ A Proxy object for AioQueue.
    
    Provides coroutines for calling 'get' and 'put' on the
    proxy.
    
    """
    @asyncio.coroutine
    def coro_get(self):
        return (yield from self._async_call('get'))

    @asyncio.coroutine
    def coro_put(self, item):
        return (yield from self._async_call('put', (item,)))


class AioAcquirerProxy(_AioProxyMixin, AcquirerProxy):
    @asyncio.coroutine
    def coro_acquire(self, blocking=True, timeout=None):
        return (yield from self._async_call('acquire', (timeout,)))


class AioBarrierProxy(_AioProxyMixin, BarrierProxy):
    @asyncio.coroutine
    def coro_wait(self, timeout=None):
        return (yield from self._async_call('wait', (timeout,)))


class AioEventProxy(_AioProxyMixin, EventProxy):
    @asyncio.coroutine
    def coro_wait(self, timeout=None):
        return (yield from self._async_call('wait', (timeout,)))


class AioConditionProxy(_AioProxyMixin, ConditionProxy):
    @asyncio.coroutine
    def coro_wait(self, timeout=None):
        return (yield from self._async_call('wait', (timeout,)))

    @asyncio.coroutine
    def coro_wait_for(self, predicate, timeout=None):
        return (yield from self._async_call('wait_for', (predicate, timeout)))


class AioManager(SyncManager):
    """ A mp.Manager that provides asyncio-friendly objects. """
    pass
AioManager.register("AioQueue", Queue, AioQueueProxy)
AioManager.register("AioBarrier", Barrier, AioQueueProxy)
AioManager.register("AioBoundedSemaphore", BoundedSemaphore, AioAcquirerProxy)
AioManager.register("AioCondition", Condition, AioConditionProxy)
AioManager.register("AioEvent", Event, AioQueueProxy)
AioManager.register("AioLock", Lock, AioAcquirerProxy)
AioManager.register("AioRLock", RLock, AioAcquirerProxy)
AioManager.register("AioSemaphore", Semaphore, AioAcquirerProxy)


def Manager():
    """ Starts and returns an asyncio-friendly mp.SyncManager. """
    m = AioManager()
    m.start()
    return m

