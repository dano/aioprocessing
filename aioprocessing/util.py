import asyncio

def run_in_executor(executor, callback, *args, **kwargs):
    loop = asyncio.get_event_loop()
    if kwargs:
        return asyncio.async(loop.run_in_executor(executor,
                                    lambda: callback(*args, **kwargs)))
    else:
        return asyncio.async(loop.run_in_executor(executor, callback, *args))


def retype_instance(recvinst, sendtype, metaklass=type):
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
    # Bases of our new instance's class should be all the current
    # bases, all of sendtype's bases, and the current type of the
    # instance
    bases = (type(recvinst),) + type(recvinst).__bases__ + sendtype.__bases__

    # We change __class__ on the instance to a new type,
    # which should match sendtype in every where, except it adds
    # the bases of recvinst (and type(recvinst)) to its bases.
    recvinst.__class__ = metaklass(sendtype.__name__, bases, {})

    # Now copy the dict of sendtype to the new type.
    dct = sendtype.__dict__
    for objname in dct:
        if not objname.startswith('__'):
            setattr(type(recvinst), objname, dct[objname])
    return recvinst

