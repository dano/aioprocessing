import multiprocessing

from . import queues
from .managers import *

def get_context(method=None):
    return multiprocessing.get_context(method=method)

def AioQueue(maxsize=0, context=None):
    if not context:
        context = multiprocessing.get_context()
    return queues.AioQueue(maxsize, ctx=context)

def AioJoinableQueue(maxsize=0, context=None):
    if not context:
        context = multiprocessing.get_context()
    return queues.AioJoinableQueue(maxsize, ctx=context)

def AioSimpleQueue(maxsize=0, context=None):
    if not context:
        context = multiprocessing.get_context()
    return queues.AioSimpleQueue(maxsize, ctx=context)
