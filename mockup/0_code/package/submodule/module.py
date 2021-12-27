import logging

def post(data:None=None, arg3:None=None, arg4:None=None) -> None:
    """post docstring
    """
    logging.info("module.post(data=%s, arg3=%s, arg4=%s)", data, arg3, arg4)
    return {
        "data": data,
        "arg3": arg3,
        "arg4": arg4
    }