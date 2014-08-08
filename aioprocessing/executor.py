import asyncio
from functools import partial
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor


class _AioExecutorMixin():
    """ A Mixin that provides asynchronous functionality.
    
    This mixin provides methods that allow a class to run
    blocking methods via asyncio in a ThreadPoolExecutor.
    It also provides methods that attempt to keep the object
    picklable despite having a non-picklable ThreadPoolExecutor
    as part of its state.
    
    """
    pool_workers = None

    def run_in_executor(self, callback, *args, **kwargs):
        """ Wraps run_in_executor so we can support kwargs.
        
        BaseEventLoop.run_in_executor does not support kwargs, so
        we wrap our callback in a lambda if kwargs are provided.
        
        """
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()

        loop = asyncio.get_event_loop()
        if kwargs:
            return loop.run_in_executor(self._executor,
                                        lambda: callback(*args, **kwargs))
        else:
            return loop.run_in_executor(self._executor, callback, *args)

    def run_in_thread(self, callback, *args, **kwargs):
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()
        fut = self._executor.submit(callback, *args, **kwargs)
        return fut.result()

    def _get_executor(self):
        return ThreadPoolExecutor(max_workers=_AioExecutorMixin.pool_workers)

    def __getstate__(self):
        state = (super().__getstate__()
                     if hasattr(super(), "__getstate__") else None)
        if not state:
            self_dict = self.__dict__
            self_dict['_executor'] = None
            return self_dict
        return state

    def __setstate__(self, state):
        if '_executor' not in state:
            super().__setstate__(state)
        else:
            self.__dict__.update(state)
        self.__dict__['_executor'] = self._get_executor()


class CoroBuilder(type):
    """ Metaclass for adding coroutines to a class.
    
    This metaclass has two main roles:
    1) Make _AioExecutorMixin a parent of the given class
    2) For every function name listed in the class attribute "coroutines",
       add a new instance method to the class called "coro_<func_name>",
       which is a asyncio.coroutine that calls func_name in a 
       ThreadPoolExecutor.
    
    """
    def __new__(cls, clsname, bases, dct):
        coro_list = dct.get('coroutines', [])
        pool_workers = dct.get('pool_workers')
        for b in bases:
            coro_list.extend(b.__dict__.get('coroutines', []))
            if not pool_workers:
                pool_workers = b.__dict__.get('pool_workers')
        if not pool_workers:
            pool_workers = cpu_count()
        _AioExecutorMixin.pool_workers = pool_workers

        # Add _AioExecutorMixin to bases.
        bases += (_AioExecutorMixin,)

        # Add coro/thread funcs to __dict__
        for func in coro_list:
            dct['coro_{}'.format(func)] = cls.coro_maker(func)
            dct['thread_{}'.format(func)] = cls.thread_maker(func)

        return super().__new__(cls, clsname, bases, dct)

    @staticmethod
    def coro_maker(func):
        def coro_func(self, *args, **kwargs):
            return (yield from self.run_in_executor(getattr(self, func), *args, **kwargs))
        return coro_func

    @staticmethod
    def thread_maker(func):
        def thread_func(self, *args, **kwargs):
            return self.run_in_thread(getattr(self, func), *args, **kwargs)
        return thread_func


