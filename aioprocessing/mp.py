# flake8: noqa
try:
    from multiprocess import *
    from multiprocess import connection, managers, util
except ImportError:
    from multiprocessing import *
    from multiprocessing import connection, managers, util
