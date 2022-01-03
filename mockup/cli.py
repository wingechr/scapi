import logging
import utils

main = utils.create_cli_main()


@main.group("mod")
def main_mod():
    pass


@main_mod.command("fun")
@utils.click.pass_context
@utils.click.argument("b", type=utils.click.INT)
@utils.click.option("--c", type=utils.click.INT, help="None", multiple=False)
@utils.click.option("--d", type=utils.click.INT, help="None", multiple=True)
@utils.input
@utils.output
def main_mod_fun(ctx, data, b: int, c: bool=None, d=None) -> None:
    """Example description
    multiline text
    
    Expect stdin data
    Writes to stdout
    """    
    return utils.encode(
        ctx.obj.api.mod.fun(
        data=utils.decode(data),
        b=b,
        c=c,
        d=d
    ))
    
    

if __name__ == '__main__':
    main()

