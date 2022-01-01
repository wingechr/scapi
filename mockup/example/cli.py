import functools

def dec(fun):
    @functools.wraps(fun)
    def fun2(*args, **kwargs):
        return fun(*args, **kwargs) + 1
    return fun2

