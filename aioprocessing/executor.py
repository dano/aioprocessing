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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._executor = self._get_executor()

    @property
    def execute(self):
        loop = asyncio.get_event_loop()
        return partial(loop.run_in_executor, self._executor)

    def _get_executor(self):
        return ThreadPoolExecutor(max_workers=cpu_count())

    def __getstate__(self):
        state = super().__getstate__() if hasattr(super(), "__getstate__") else None
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

