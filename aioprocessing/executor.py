import asyncio
from functools import partial
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor


class CoroBuilder(type):
    def __new__(cls, clsname, bases, dct):
        coro_list = dct.get('coroutines', [])
        for b in bases:
            coro_list.extend(b.__dict__.get('coroutines', []))
        for func in coro_list:
            dct['coro_{}'.format(func)] = cls.coro_maker(func)

        return super().__new__(cls, clsname, bases, dct)

    @staticmethod
    def coro_maker(func):
        def coro_func(self, *args, **kwargs):
            return (yield from self.execute(getattr(self, func), *args, **kwargs))
        return coro_func


class _AioExecutorMixin():
    """ A Mixin that provides asynchronous functionality.
    
    This mixin provides methods that allow a class to run
    blocking methods via asyncio in a ThreadPoolExecutor.
    It also provides methods that attempt to keep the object
    picklable despite having a non-picklable ThreadPoolExecutor
    as part of its state.
    
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._executor = self._get_executor()

    @property
    def execute(self):
        return partial(self.run_in_executor, self._executor)

    def run_in_executor(self, executor, callback, *args, **kwargs):
        """ Wraps run_in_executor so we can support kwargs.
        
        BaseEventLoop.run_in_executor does not support kwargs, so
        we wrap our callback in a lambda if kwargs are provided.
        
        """
        loop = asyncio.get_event_loop()
        if kwargs:
            return loop.run_in_executor(executor,
                                        lambda: callback(*args, **kwargs))
        else:
            return loop.run_in_executor(executor, callback, *args)

    def _get_executor(self):
        return ThreadPoolExecutor(max_workers=cpu_count())

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

