import multiprocessing

from .managers import *
from . import executor


def get_context(method=None):
    return multiprocessing.get_context(method=method)

class AioProcess(metaclass=executor.CoroBuilder):
    coroutines = ['join']

def merge_instance(recvinst, sendtype, metaklass):
    """ Turn recvinst into an instance of sendtype.
    
    Given an instance (recvinst) of some class, turn that instance 
    into an instance of class `sendtype`, which inherits from 
    type(recvinst). The output instance will still retain all
    the instance methods and attributes it started with, however.

    For example:

    Input:
    type(recvinst) == Connection
    sendtype == AioConnection
    metaklass == CoroBuilder (metaclass used for creating AioConnection)

    Output:
    recvinst.__class__ == AioConnection
    recvinst.__bases__ == bases_of_AioConnection +
                          Connection + bases_of_Connection
    
    
    """
    bases = (type(recvinst),) + type(recvinst).__bases__ + sendtype.__bases__
    # We change __class__ on the instance by creatin
    recvinst.__class__ = metaklass(sendtype.__name__, bases, {})
    dct = sendtype.__dict__
    for objname in dct:
        if not objname.startswith('__'):
            setattr(type(recvinst), objname, dct[objname])
    return recvinst

def AioPipe(duplex=True):
    from .connection import AioConnection
    conn1, conn2 = multiprocessing.Pipe(duplex=duplex)
    # We want to turn whatever type of Connection object returned
    # by multiprocessing into an instance of AioConnection.
    # We do that by giving the instance new base classes, via
    # reassigning __class__. We add the AioConnection base classes
    # to the current instance.
    conn1 = merge_instance(conn1, AioConnection, executor.CoroBuilder)
    conn2 = merge_instance(conn2, AioConnection, executor.CoroBuilder)
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

