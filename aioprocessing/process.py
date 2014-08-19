from .executor import CoroBuilder

class AioProcess(metaclass=CoroBuilder):
    delegate = Process
    coroutines = ['join']
