import logging
import utils

__version__ = "0.1.0"

main = utils.create_cli_main(__version__)


@main.group("mod")
@utils.click.pass_context
def main_mod(ctx):
    pass


@main_mod.command("fun")
@utils.click.pass_context
@utils.click.argument("b", type=utils.click.types.INT)
@utils.click.option("--c", is_flag=True, help="desc")
@utils.click.option("--d", type=utils.click.types.INT, multiple=True, help="desc")
@utils.input_stdin
@utils.output_stdout
def main_mod_fun(ctx, data: object, b: int, c: bool = None, d: list = None) -> object:
    """Example description
    multiline text"""
    return utils.encode_content(
        ctx.obj.api.mod.fun(
            data=utils.decode_content(data, "application/json; charset=utf8; schema="),
            b=b,
            c=c,
            d=d,
        ),
        "application/json; charset=utf8; schema=output_schema",
    )


if __name__ == "__main__":
    main()
