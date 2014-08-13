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

__all__ = ['Manager']

AioBaseQueueProxy = MakeProxyType('AioQueueProxy', (
    'task_done', 'get', 'qsize', 'put', 'put_nowait', 
    'get_nowait', 'empty', 'join', '_qsize', 'full'
    ))


class _AioProxyMixin:
    def _async_call(self, method, args=()):
        return asyncio.async(self.run_in_executor(self._callmethod, method, args))

    def run_in_executor(self, callback, *args, **kwargs):
        """ Wraps run_in_executor so we can support kwargs.
        
        BaseEventLoop.run_in_executor does not support kwargs, so
        we wrap our callback in a lambda if kwargs are provided.
        
        """
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()

        return util.run_in_executor(self._executor, callback, *args, **kwargs)

    def run_in_thread(self, callback, *args, **kwargs):
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()
        fut = self._executor.submit(callback, *args, **kwargs)
        return fut.result()

    def _get_executor(self):
        return ThreadPoolExecutor(max_workers=_AioExecutorMixin.pool_workers)


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
            return asyncio.async(self._async_call(func, args))
        return coro_func


class AioQueueProxy(AioBaseQueueProxy, metaclass=ProxyCoroBuilder):
    """ A Proxy object for AioQueue.
    
    Provides coroutines for calling 'get' and 'put' on the
    proxy.
    
    """
    #delegate = AioBaseQueueProxy
    coroutines = ['get', 'put']


class AioAcquirerProxy(AcquirerProxy, metaclass=CoroBuilder):
    #delegate = AcquirerProxy
    coroutines = ['acquire']


class AioBarrierProxy(BarrierProxy, metaclass=CoroBuilder):
    #delegate = BarrierProxy
    coroutines = ['wait']


class AioEventProxy(EventProxy, metaclass=CoroBuilder):
    #delegate = EventProxy
    coroutines = ['wait']


class AioConditionProxy(ConditionProxy, metaclass=CoroBuilder):
    #delegate = ConditionProxy
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

