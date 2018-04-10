from multiprocessing import Process

from .executor import CoroBuilder

__all__ = ['AioProcess']


class AioProcess(metaclass=CoroBuilder):
    delegate = Process
    coroutines = ['join']
