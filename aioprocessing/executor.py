from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from . import util


class _AioExecutorMixin():
    """ A Mixin that provides asynchronous functionality.
    
    This mixin provides methods that allow a class to run
    blocking methods via asyncio in a ThreadPoolExecutor.
    It also provides methods that attempt to keep the object
    picklable despite having a non-picklable ThreadPoolExecutor
    as part of its state.
    
    """
    pool_workers = None
    delegate = None

    def __init__(self, *args, **kwargs):
        if self.delegate:
            self._obj = self.delegate(*args, **kwargs)
        else:
            self._obj = None

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

    def __getattr__(self, attr):
        if (self._obj and hasattr(self._obj, attr) and
            not attr.startswith("__")):
            return getattr(self._obj, attr)
        raise AttributeError

    def __getstate__(self):
        self_dict = self.__dict__
        self_dict['_executor'] = None
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._executor = self._get_executor()


class CoroBuilder(type):
    """ Metaclass for adding coroutines to a class.
    
    This metaclass has two main roles:
    1) Make _AioExecutorMixin a parent of the given class
    2) For every function name listed in the class attribute "coroutines",
       add a new instance method to the class called "coro_<func_name>",
       which is a asyncio.coroutine that calls func_name in a
       ThreadPoolExecutor.
    
    """
    def __new__(cls, clsname, bases, dct, **kwargs):
        coro_list = dct.get('coroutines', [])
        pool_workers = dct.get('pool_workers')
        existing_coros = set()

        def find_existing_coros(d):
            for attr in d:
                if attr.startswith("coro_") or attr.startswith("thread_"):
                    existing_coros.add(attr)

        find_existing_coros(dct)
        for b in bases:
            coro_list.extend(b.__dict__.get('coroutines', []))
            if not pool_workers:
                pool_workers = b.__dict__.get('pool_workers')
            find_existing_coros(b.__dict__)

        if not pool_workers:
            pool_workers = cpu_count()
        _AioExecutorMixin.pool_workers = pool_workers

        # Add _AioExecutorMixin to bases.
        if _AioExecutorMixin not in bases:
            bases += (_AioExecutorMixin,)

        # Add coro funcs to dct, but only if a definition
        # is not already provided by dct or one of its bases.
        for func in coro_list:
            coro_name = 'coro_{}'.format(func)
            if coro_name not in existing_coros:
                dct[coro_name] = cls.coro_maker(func)

        return super().__new__(cls, clsname, bases, dct)

    @staticmethod
    def coro_maker(func):
        def coro_func(self, *args, **kwargs):
            return self.run_in_executor(getattr(self, func), *args, **kwargs)
        return coro_func
