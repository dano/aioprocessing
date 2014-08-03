import asyncio
from queue import Queue
from threading import (Barrier, BoundedSemaphore, Condition, Event,
                       Lock, RLock, Semaphore)
from multiprocessing.managers import (SyncManager, BaseProxy, MakeProxyType,
                                      BarrierProxy, EventProxy, ConditionProxy,
                                      AcquirerProxy)

from . import queues
from .executor import _AioExecutorMixin, CoroBuilder

__all__ = ['Manager']

AioBaseQueueProxy = MakeProxyType('AioQueueProxy', (
    'task_done', 'get', 'qsize', 'put', 'put_nowait', 
    'get_nowait', 'empty', 'join', '_qsize', 'full'
    ))


class _AioProxyMixin(_AioExecutorMixin):
    @asyncio.coroutine
    def _async_call(self, method, args=()):
        return (yield from self.execute(self._callmethod, method, args))

class ProxyCoroBuilder(type):
    """ Build coroutines to proxy functions. """
    def __new__(cls, clsname, bases, dct):
        coro_list = dct.get('coroutines', [])
        for b in bases:
            coro_list.extend(b.__dict__.get('coroutines', []))
        bases += (_AioProxyMixin,)
        for func in coro_list:
            dct['coro_{}'.format(func)] = cls.coro_maker(func)

        return super().__new__(cls, clsname, bases, dct)

    @staticmethod
    def coro_maker(func):
        def coro_func(self, *args):
            return (yield from self._async_call(func, args))
        return coro_func

class AioQueueProxy(AioBaseQueueProxy, metaclass=ProxyCoroBuilder):
    """ A Proxy object for AioQueue.
    
    Provides coroutines for calling 'get' and 'put' on the
    proxy.
    
    """
    coroutines = ['get', 'put']


class AioAcquirerProxy(AcquirerProxy, metaclass=CoroBuilder):
    coroutines = ['acquire']


class AioBarrierProxy(BarrierProxy, metaclass=CoroBuilder):
    coroutines = ['wait']


class AioEventProxy(EventProxy, metaclass=CoroBuilder):
    coroutines = ['wait']


class AioConditionProxy(ConditionProxy, metaclass=CoroBuilder):
    coroutines = ['wait', 'wait_for']


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

