import multiprocessing
from multiprocessing import get_context

from .managers import *
from .connection import *
from .util import retype_instance
from .executor import CoroBuilder

__all__ = ['AioProcess', 'AioPipe', 'AioQueue', 'AioJoinableQueue', 
           'AioSimpleQueue', 'AioLock', 'AioRLock', 'AioCondition', 
           'AioSemaphore', 'AioBoundedSemaphore', 'AioEvent', 'AioBarrier']
__all__.extend(managers.__all__)


class AioProcess(metaclass=CoroBuilder):
    coroutines = ['join']


def AioPipe(duplex=True):
    from .connection import AioConnection
    conn1, conn2 = multiprocessing.Pipe(duplex=duplex)
    # Transform the returned connection instances into
    # instance of AioConnection.
    conn1 = AioConnection(conn1)
    conn2 = AioConnection(conn2)
    #conn1 = retype_instance(conn1, AioConnection, CoroBuilder)
    #conn2 = retype_instance(conn2, AioConnection, CoroBuilder)
    return conn1, conn2

# queues

def AioQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.Queue
    
    Returns an AioQueue objects with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = get_context()
    from .queues import AioQueue
    return AioQueue(maxsize, ctx=context)

def AioJoinableQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.JoinableQueue
    
    Returns an AioJoinableQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = get_context()
    from .queues import AioJoinableQueue
    return AioJoinableQueue(maxsize, ctx=context)

def AioSimpleQueue(context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.SimpleQueue
    
    Returns an AioSimpleQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    if not context:
        context = get_context()
    from .queues import AioSimpleQueue
    return AioSimpleQueue(ctx=context)

# locks

def AioLock(context=None):
    '''Returns a non-recursive lock object'''
    if not context:
        context = get_context()
    from .locks import AioLock
    return AioLock(ctx=get_context())

def AioRLock(context=None):
    '''Returns a recursive lock object'''
    if not context:
        context = get_context()
    from .locks import AioRLock
    return AioRLock(ctx=get_context())

def AioCondition(lock=None, context=None):
    '''Returns a condition object'''
    if not context:
        context = get_context()
    from .locks import AioCondition
    return AioCondition(lock, ctx=get_context())

def AioSemaphore(value=1, context=None):
    '''Returns a semaphore object'''
    if not context:
        context = get_context()
    from .locks import AioSemaphore
    return AioSemaphore(value, ctx=get_context())

def AioBoundedSemaphore(value=1, context=None):
    '''Returns a bounded semaphore object'''
    if not context:
        context = get_context()
    from .locks import AioBoundedSemaphore
    return AioBoundedSemaphore(value, ctx=get_context())

def AioEvent(context=None):
    '''Returns an event object'''
    if not context:
        context = get_context()
    from .locks import AioEvent
    return AioEvent(ctx=get_context())

def AioBarrier(parties, action=None, timeout=None, context=None):
    '''Returns a barrier object'''
    if not context:
        context = get_context()
    from .locks import AioBarrier
    return AioBarrier(parties, action, timeout, ctx=context)

