
@route("GET", ["get"], [], None)
def route_get(arg1: list=None, arg2: list=None) -> bytes:
    """Example description
    multiline text
    Args:
        arg1(list)
        arg2(list)
    Returns:
        bytes
    """
    return api.get(
        arg1=arg1,
        arg2=arg2
    )

@route("POST", ["module", "submodule", "post"], [], "data")
def route_module_submodule_post(data: bytes, arg3: list=None, arg4: list=None) -> bytes:
    """bla b
    Args:
        data(bytes)
        arg3(list): blabla text arg3
        arg4(list)
    Returns:
        bytes
    """
    return api.module.submodule.post(
        data=data,
        arg3=arg3,
        arg4=arg4
    )

@route("GET", ["rest", "resource"], [], None)
def route_rest_resource_list() -> bytes:
    """None
    Returns:
        bytes
    """
    return api.rest.resource.list(
    )

@route("POST", ["rest", "resource"], [], "data")
def route_rest_resource_post(data: bytes) -> bytes:
    """None
    Args:
        data(bytes)
    Returns:
        bytes
    """
    return api.rest.resource.post(
        data=data
    )

@route("GET", ["rest", "resource"], ["pk"], None)
def route_rest_resource_get(pk: list) -> bytes:
    """None
    Args:
        pk(list)
    Returns:
        bytes
    """
    return api.rest.resource.get(
        pk=pk
    )

@route("DELETE", ["rest", "resource"], ["pk"], None)
def route_rest_resource_delete(pk: list) -> None:
    """None
    Args:
        pk(list)
    """
    api.rest.resource.delete(
        pk=pk
    )

@route("PUT", ["rest", "resource"], ["pk"], "data")
def route_rest_resource_put(data: bytes, pk: list) -> None:
    """None
    Args:
        data(bytes)
        pk(list)
    """
    api.rest.resource.put(
        data=data,
        pk=pk
    )

@route("PATCH", ["rest", "resource"], ["pk"], "data")
def route_rest_resource_patch(data: bytes, pk: list) -> None:
    """None
    Args:
        data(bytes)
        pk(list)
    """
    api.rest.resource.patch(
        data=data,
        pk=pk
    )