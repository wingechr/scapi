
@main.command("get")
@click.option("--arg1", click.int, help="None")
@click.option("--arg2", click.str, help="None")
def main_get(arg1: int=None, arg2: str=None) -> None:
    """Example description
    multiline text
    Args:
        arg1(int)
        arg2(str)
    """
    api.get(
        arg1=arg1,
        arg2=arg2
    )

@main.group("module")
def main_module():
    pass


@main_module.group("submodule")
def main_module_submodule():
    pass


@main_module_submodule.command("post")
@click.option("--arg3", click.str, help="blabla text arg3")
@click.option("--arg4", click.float, help="None")
def main_module_submodule_post(arg3: str=1, arg4: float=None) -> None:
    """bla b
    Args:
        arg3(str): blabla text arg3 Defaults to 1
        arg4(float)
    """
    api.module.submodule.post(
        arg3=arg3,
        arg4_orig=arg4
    )

@main.group("rest")
def main_rest():
    pass


@main_rest.group("resource")
def main_rest_resource():
    pass


@main_rest_resource.command("list")
def main_rest_resource_list() -> None:
    """None
    """
    api.rest.resource.list(
    )

@main_rest_resource.command("post")
def main_rest_resource_post() -> None:
    """None
    """
    api.rest.resource.post(
    )

@main_rest_resource.command("get")
@click.argument("pk", click.int)
def main_rest_resource_get(pk: int) -> None:
    """None
    Args:
        pk(int)
    """
    api.rest.resource.get(
        pk=pk
    )

@main_rest_resource.command("delete")
@click.argument("pk", click.int)
def main_rest_resource_delete(pk: int) -> None:
    """None
    Args:
        pk(int)
    """
    api.rest.resource.delete(
        pk=pk
    )

@main_rest_resource.command("put")
@click.argument("pk", click.int)
def main_rest_resource_put(pk: int) -> None:
    """None
    Args:
        pk(int)
    """
    api.rest.resource.put(
        pk=pk
    )

@main_rest_resource.command("patch")
@click.argument("pk", click.int)
def main_rest_resource_patch(pk: int) -> None:
    """None
    Args:
        pk(int)
    """
    api.rest.resource.patch(
        pk=pk
    )