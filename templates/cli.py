#!/usr/bin/env python3

import logging
import os
import sys
import importlib

import click
import coloredlogs


__version__ = '0.0.0'

@click.group()
@click.pass_context
@click.version_option(__version__)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="debug",
)
@click.argument(
    "module"   
)
@click.option(
    "--host",
    "-h",
    default="http://localhost:8000",
)
def main(ctx, loglevel, module, host):
    if isinstance(loglevel, str):
        loglevel = getattr(logging, loglevel.upper())
    coloredlogs.DEFAULT_LOG_FORMAT = "[%(asctime)s %(levelname)7s] %(message)s"
    coloredlogs.DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    # NOTE: black + biold = gray
    coloredlogs.DEFAULT_FIELD_STYLES = {
        'asctime': {'color': 'black', 'bold': True},
        'levelname': {'color': 'black', 'bold': True}
    }
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        'debug': {'color': 'black', 'bold': True},
        'info': {'color': 'white'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red', 'bold': 10}
    }
    coloredlogs.install(level=loglevel)
    ctx.ensure_object(dict)

    logging.debug("loading module: %s", module)
    ctx.obj["api"] = getattr(importlib.import_module(module, package=None), "api")(host=host)

    ctx.obj["stdin"] = sys.stdin.buffer
    ctx.obj["stdout"] = sys.stdout.buffer
    


'''{{click_functions}}'''

if __name__ == "__main__":
    main(prog_name="PROGRAM_NAME")