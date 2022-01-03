
@main.group("mod")
def main_mod():
    pass


@main_mod.command("fun")
@click.argument("b", click.int)
@click.option("--c", click.bool, help="None")
@click.option("--d", click.int, help="None")
def main_mod_fun(b: int, c: bool=None, d: int=None) -> None:
    """Example description
    multiline text
    
    Args:
        b(int): TODO: description
        c(bool): TODO: description
        d(int): TODO: description
    """
    api.mod.fun(
        b=b,
        c=c,
        d=d
    )