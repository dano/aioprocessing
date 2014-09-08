import multiprocessing

from .connection import *
from .managers import *

__all__ = ['AioProcess', 'AioManager', 'AioPipe', 'AioQueue', 'AioSimpleQueue',
           'AioJoinableQueue', 'AioLock', 'AioRLock', 'AioCondition', 'AioPool',
           'AioSemaphore', 'AioBoundedSemaphore', 'AioEvent', 'AioBarrier']

version = "0.0.1"
version_info = (0, 0, 1)

def AioProcess(*args, context=None, **kwargs):
    context = context if context else multiprocessing.get_context()
    from .process import AioProcess
    return AioProcess(*args, **kwargs)

def AioPool(*args, context=None, **kwargs):
    context = context if context else multiprocessing.get_context()
    from .pool import AioPool
    return AioPool(*args, **kwargs)

def AioManager(context=None):
    """ Starts and returns an asyncio-friendly mp.SyncManager. """
    context = context if context else multiprocessing.get_context()
    from .managers import AioSyncManager
    m = AioSyncManager(ctx=context)
    m.start()
    return m

def AioPipe(duplex=True):
    from .connection import AioConnection
    conn1, conn2 = multiprocessing.Pipe(duplex=duplex)
    # Transform the returned connection instances into
    # instance of AioConnection.
    conn1 = AioConnection(conn1)
    conn2 = AioConnection(conn2)
    return conn1, conn2

# queues

def AioQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.Queue
    
    Returns an AioQueue objects with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    context = context = context if context else multiprocessing.get_context()
    from .queues import AioQueue
    return AioQueue(maxsize, ctx=context)

def AioJoinableQueue(maxsize=0, context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.JoinableQueue
    
    Returns an AioJoinableQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    context = context = context if context else multiprocessing.get_context()
    from .queues import AioJoinableQueue
    return AioJoinableQueue(maxsize, ctx=context)

def AioSimpleQueue(context=None):
    """ Returns an asyncio-friendly version of a multiprocessing.SimpleQueue
    
    Returns an AioSimpleQueue object with the given context. If a context
    is not provided, the default for the platform will be used.
    
    """
    context = context = context if context else multiprocessing.get_context()
    from .queues import AioSimpleQueue
    return AioSimpleQueue(ctx=context)

# locks

def AioLock(context=None):
    '''Returns a non-recursive lock object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioLock
    return AioLock(ctx=context)

def AioRLock(context=None):
    '''Returns a recursive lock object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioRLock
    return AioRLock(ctx=context)

def AioCondition(lock=None, context=None):
    '''Returns a condition object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioCondition
    return AioCondition(lock, ctx=context)

def AioSemaphore(value=1, context=None):
    '''Returns a semaphore object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioSemaphore
    return AioSemaphore(value, ctx=context)

def AioBoundedSemaphore(value=1, context=None):
    '''Returns a bounded semaphore object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioBoundedSemaphore
    return AioBoundedSemaphore(value, ctx=context)

def AioEvent(context=None):
    '''Returns an event object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioEvent
    return AioEvent(ctx=context)

def AioBarrier(parties, action=None, timeout=None, context=None):
    '''Returns a barrier object'''
    context = context = context if context else multiprocessing.get_context()
    from .locks import AioBarrier
    return AioBarrier(parties, action, timeout, ctx=context)


