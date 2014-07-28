import multiprocessing

AsyncContext(object):
    def __init__(self, name):
        self.name = name
        self.ctx = multiprocessing.get_context(name)
