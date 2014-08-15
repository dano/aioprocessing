import multiprocessing
from multiprocessing.connection import (Listener, Client, deliver_challenge,
                                        answer_challenge, wait)

from .executor import CoroBuilder
from .util import run_in_executor

__all__ = ['AioConnection']


class AioConnection(metaclass=CoroBuilder):
    coroutines = ['recv', 'poll', 'send_bytes', 'recv_bytes',
                  'recv_bytes_into']

    def __init__(self, obj):
        super().__init__()
        self._obj = obj

def AioClient(*args, **kwargs):
    conn = Client(*args, **kwargs)
    return AioConnection(conn)


class AioListener(metaclass=CoroBuilder):
    delegate = Listener
    coroutines = ['accept']


def coro_deliver_challenge(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, deliver_challenge, *args, **kwargs)

def coro_answer_challenge(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, answer_challenge, *args, **kwargs)


def coro_wait(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, wait, *args, **kwargs)

