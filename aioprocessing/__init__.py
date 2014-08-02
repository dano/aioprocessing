import multiprocessing

from .managers import *


def get_context(method=None):
    return multiprocessing.get_context(method=method)

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

def AioLock(self, context=None):
    '''Returns a non-recursive lock object'''
    if not context:
        context = get_context()
    from .synchronize import AioLock
    return AioLock(ctx=self.get_context())

def AioRLock(self, context=None):
    '''Returns a recursive lock object'''
    if not context:
        context = get_context()
    from .locks import RLock
    return RLock(ctx=self.get_context())

def AioCondition(self, lock=None, context=None):
    '''Returns a condition object'''
    if not context:
        context = get_context()
    from .locks import AioCondition
    return AioCondition(lock, ctx=self.get_context())

def AioSemaphore(self, value=1, context=None):
    '''Returns a semaphore object'''
    if not context:
        context = get_context()
    from .locks import AioSemaphore
    return AioSemaphore(value, ctx=self.get_context())

def AioBoundedSemaphore(self, value=1, context=None):
    '''Returns a bounded semaphore object'''
    if not context:
        context = get_context()
    from .locks import BoundedSemaphore
    return BoundedSemaphore(value, ctx=self.get_context())

def AioEvent(self, context=None):
    '''Returns an event object'''
    if not context:
        context = get_context()
    from .locks import AioEvent
    return AioEvent(ctx=self.get_context())

def AioBarrier(self, parties, action=None, timeout=None, context=None):
    '''Returns a barrier object'''
    if not context:
        context = get_context()
    from .locks import AioBarrier
    return AioBarrier(parties, action, timeout, ctx=context)

