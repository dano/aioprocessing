from multiprocessing import cpu_count
from functools import partial, wraps
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
    pool_workers = cpu_count()

    def run_in_executor(self, callback, *args, **kwargs):
        """ Wraps run_in_executor so we can support kwargs.
        
        BaseEventLoop.run_in_executor does not support kwargs, so
        we wrap our callback in a lambda if kwargs are provided.
        
        """
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()

        return util.run_in_executor(self._executor, callback, *args, **kwargs)

    def run_in_thread(self, callback, *args, **kwargs):
        """ Runs a method in an executor thread.
        
        This is used when a method must be run in a thread (e.g.
        to that a lock is released in the same thread it was
        acquired), but should be run in a blocking way.
        
        """
        if not hasattr(self, '_executor'):
            self._executor = self._get_executor()
        fut = self._executor.submit(callback, *args, **kwargs)
        return fut.result()

    def _get_executor(self):
        return ThreadPoolExecutor(max_workers=self.pool_workers)

    def __getattr__(self, attr):
        if (self._obj and hasattr(self._obj, attr) and
            not attr.startswith("__")):
            return getattr(self._obj, attr)
        raise AttributeError(attr)

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
        existing_coros = set()

        def find_existing_coros(d):
            for attr in d:
                if attr.startswith("coro_") or attr.startswith("thread_"):
                    existing_coros.add(attr)

        find_existing_coros(dct)
        for b in bases:
            b_dct = b.__dict__
            coro_list.extend(b_dct.get('coroutines', []))
            find_existing_coros(b_dct)

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

    def __init__(cls, name, bases, dct):
        """ Properly initialize a coroutine wrapper.
        
        Sets pool_workers and delegate on the class, and also
        adds an __init__ method to it that instantiates the
        delegate with the proper context.
        
        """
        super().__init__(name, bases, dct)
        pool_workers = dct.get('pool_workers')
        delegate = dct.get('delegate')
        old_init = dct.get('__init__')
        for b in bases:
            b_dct = b.__dict__
            if not pool_workers:
                pool_workers = b_dct.get('pool_workers')
            if not delegate:
                delegate = b_dct.get('delegate')
            if not old_init:
                old_init = b_dct.get('__init__')

        if not pool_workers:
            pool_workers = cpu_count()

        cls.delegate = delegate
        # If we found a value for pool_workers, set it. If not,
        # AioExecutorMixin sets a default that will be used.
        if pool_workers:
            cls.pool_workers = pool_workers

        # Here's the __init__ we want every wrapper class to use.
        # It just instantiates the delegate mp object using the 
        # correct context.
        @wraps(old_init)
        def init_func(self, *args, **kwargs):
            # Be sure to call the original __init__, if there
            # was one.
            if old_init:
                old_init(self, *args, **kwargs)
            # If we're wrapping a mp object, instantiate it here.
            # If a context was specified, we instaniate the mp class
            # using that context. Otherwise, we'll just use the default
            # context.
            if self.delegate:
                ctx = kwargs.pop('ctx', None)
                if ctx:
                    cls = getattr(ctx, self.delegate.__name__)
                else:
                    cls = self.delegate
                self._obj = cls(*args, **kwargs)
        cls.__init__ = init_func

    @staticmethod
    def coro_maker(func):
        def coro_func(self, *args, **kwargs):
            return self.run_in_executor(getattr(self, func), *args, **kwargs)
        return coro_func

