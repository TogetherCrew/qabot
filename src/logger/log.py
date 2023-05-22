import functools
import logging
from contextlib import contextmanager
import inspect
# logging.basicConfig(level=logging.INFO)


import logging
from contextlib import contextmanager
from typing import Union


@contextmanager
def log_level(level, name: str):
    logging.basicConfig()
    name = name.upper() if name else None
    logger = logging.getLogger(name)

    # old_handlers = logger.handlers.copy()  # Save the original handlers
    # logger.handlers.clear()
    if logger.hasHandlers():  # remove all previous handlers. Without this -> duplicated logs and without format
        logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s: %(message)s', datefmt='%I:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    logger.propagate = True

    try:
        yield logger
    finally:
        logger.setLevel(old_level)
        logger.handlers.clear()  # Clear the handlers added by this context manager
        # logger.handlers.extend(old_handlers)  # Restore the original handlers


def log_with_level(level=logging.NOTSET, name: str = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            new_name = name.upper() if name else func.__name__
            with log_level(level, new_name):
                return func(*args, log=log(new_name), **kwargs)
        return wrapper
    return decorator


def log(name: str = None):
    return logging.getLogger(name.upper() if name else None)


def logf():
    return log(inspect.stack()[1][3].upper())


@log_with_level(logging.DEBUG)
def my_func(**kwargs):

    kwargs.get('log').debug('This is a debug message')


my_func()
