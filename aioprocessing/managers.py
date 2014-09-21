import asyncio
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import (Barrier, BoundedSemaphore, Condition, Event,
                       Lock, RLock, Semaphore)
from multiprocessing.managers import (SyncManager, BaseProxy, MakeProxyType,
                                      BarrierProxy, EventProxy, ConditionProxy,
                                      AcquirerProxy)

from . import queues
from . import util
from .executor import _AioExecutorMixin, CoroBuilder


AioBaseQueueProxy = MakeProxyType('AioQueueProxy', (
    'task_done', 'get', 'qsize', 'put', 'put_nowait', 
    'get_nowait', 'empty', 'join', '_qsize', 'full'
    ))


class _AioProxyMixin(_AioExecutorMixin):
    _obj = None

    def _async_call(self, method, *args, loop=None, **kwargs):
        return asyncio.async(self.run_in_executor(self._callmethod, method, 
                                                  args, kwargs, loop=loop))


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
        def coro_func(self, *args, loop=None, **kwargs):
            return self._async_call(func, *args, loop=loop, 
                                    **kwargs)
        return coro_func


class AioQueueProxy(AioBaseQueueProxy, metaclass=ProxyCoroBuilder):
    """ A Proxy object for AioQueue.
    
    Provides coroutines for calling 'get' and 'put' on the
    proxy.
    
    """
    #delegate = AioBaseQueueProxy
    coroutines = ['get', 'put']


class AioAcquirerProxy(AcquirerProxy, metaclass=ProxyCoroBuilder):
    #delegate = AcquirerProxy
    coroutines = ['acquire', 'release']


class AioBarrierProxy(BarrierProxy, metaclass=ProxyCoroBuilder):
    #delegate = BarrierProxy
    coroutines = ['wait']


class AioEventProxy(EventProxy, metaclass=ProxyCoroBuilder):
    #delegate = EventProxy
    coroutines = ['wait']


class AioConditionProxy(ConditionProxy, metaclass=ProxyCoroBuilder):
    #delegate = ConditionProxy
    coroutines = ['wait', 'wait_for']


class AioSyncManager(SyncManager):
    """ A mp.Manager that provides asyncio-friendly objects. """
    pass

AioSyncManager.register("AioQueue", Queue, AioQueueProxy)
AioSyncManager.register("AioBarrier", Barrier, AioQueueProxy)
AioSyncManager.register("AioBoundedSemaphore", BoundedSemaphore, AioAcquirerProxy)
AioSyncManager.register("AioCondition", Condition, AioConditionProxy)
AioSyncManager.register("AioEvent", Event, AioQueueProxy)
AioSyncManager.register("AioLock", Lock, AioAcquirerProxy)
AioSyncManager.register("AioRLock", RLock, AioAcquirerProxy)
AioSyncManager.register("AioSemaphore", Semaphore, AioAcquirerProxy)

