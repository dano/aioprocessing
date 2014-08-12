import asyncio

from .executor import _AioExecutorMixin, CoroBuilder
from  multiprocessing.synchronize import (Event, Lock, RLock, BoundedSemaphore,
                                          Condition, Semaphore, Barrier)

__all__ = ["AioLock", "AioRLock", "AioBarrier", "AioCondition", "AioEvent",
           "AioSemaphore", "AioBoundedSemaphore"]


class _ContextManager:
    """Context manager.

    This enables the following idiom for acquiring and releasing a
    lock around a block:

        with (yield from lock):
            <block>

    while failing loudly when accidentally using:

        with lock:
            <block>
    """

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        # We have no use for the "as ..."  clause in the with
        # statement for locks.
        return None

    def __exit__(self, *args):
        try:
            self._lock.thread_release()
        finally:
            self._lock = None  # Crudely prevent reuse.


class AioBaseLock(metaclass=CoroBuilder):
    pool_workers = 1
    coroutines = ['acquire', 'release']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._threaded_acquire = False
        # We can't use super to call these, perhaps because they're
        # implemented in C.
        self._parent_release = super().__getattribute__('release')
        self._parent_acquire = super().__getattribute__('acquire')

    def coro_acquire(self, *args, **kwargs):
        self._threaded_acquire = True
        return self.run_in_executor(self.acquire, *args, **kwargs)

    def release(self):
        if self._threaded_acquire:
            return self.run_in_thread(self._parent_release)
        return self._parent_release()

    def coro_release(self):
        if not self._threaded_acquire:
            raise RuntimeError("A lock acquired via acquire() "
                               "must be released via release().")
        else:
            self._threaded_acquire = False
            return self.run_in_executor(self._parent_release)


    def __iter__(self):
        yield from self.coro_acquire()
        return _ContextManager(self)


class AioBaseWaiter(metaclass=CoroBuilder):
    pool_workers = 1
    coroutines = ['wait']


class AioBarrier(Barrier, AioBaseWaiter):
    pass


class AioCondition(AioBaseWaiter, AioBaseLock, Condition):
    concrete=Condition
    pool_workers = 1
    coroutines = ['wait_for', 'notify', 'notify_all']


class AioEvent(AioBaseWaiter, Event):
    pass


class AioLock(AioBaseLock, Lock):
    pass


class AioRLock(AioBaseLock, RLock):
    pass


class AioSemaphore(AioBaseLock, Semaphore):
    pass


class AioBoundedSemaphore(AioBaseLock, BoundedSemaphore):
    pass


