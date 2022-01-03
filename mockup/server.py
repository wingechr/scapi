
@route("POST", ["mod", "fun"], ["b"], "data")
def route_mod_fun(data: bytes, b: list, c: list=None, d: list=None) -> bytes:
    """Example description
    multiline text
    
    Args:
        data(bytes): TODO: description
        b(list): TODO: description
        c(list): TODO: description
        d(list): TODO: description
    
    Returns:
        bytes
    """
    return api.mod.fun(
        data=data,
        b=b,
        c=c,
        d=d
    )