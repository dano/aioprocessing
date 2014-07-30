import multiprocessing

from . import queues
from .managers import *


def get_context(method=None):
    return multiprocessing.get_context(method=method)

def AioQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.Queue
    
    Returns an AioQueue objects with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = multiprocessing.get_context()
    return queues.AioQueue(maxsize, ctx=context)

def AioJoinableQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.JoinableQueue
    
    Returns an AioJoinableQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = multiprocessing.get_context()
    return queues.AioJoinableQueue(maxsize, ctx=context)

def AioSimpleQueue(context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.SimpleQueue
    
    Returns an AioSimpleQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = multiprocessing.get_context()
    return queues.AioSimpleQueue(ctx=context)
