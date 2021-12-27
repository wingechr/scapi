from .utils import logging

my_schema = {"a": 1}

def get(arg1:None=1, arg2:my_schema=None) -> my_schema:
    """get docstring
    """
    logging.info("module.get(arg1=%s, arg2=%s)", arg1, arg2)
    return {
        "arg1": arg1,
        "arg2": arg2
    }

