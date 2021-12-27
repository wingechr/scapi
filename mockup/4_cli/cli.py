#!/usr/bin/env python3

import logging

# environment for imports
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../1_api')
sys.path.append(os.path.dirname(__file__) + '/../3_client')

from api import api
#from client import api

import click
import coloredlogs


coloredlogs.DEFAULT_LOG_FORMAT = "[%(asctime)s %(levelname)7s] %(message)s"
coloredlogs.DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
coloredlogs.DEFAULT_FIELD_STYLES = {
    'asctime': {'color': 'black', 'bold': True}, # gray
    'levelname': {'color': 'black', 'bold': True} # gray
}
coloredlogs.DEFAULT_LEVEL_STYLES = {
    'debug': {'color': 'black', 'bold': True}, # gray
    'info': {'color': 'white'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red', 'bold': 10}
}



@click.group()
@click.pass_context
#@click.version_option(__version__)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
)
def main(ctx, loglevel):
    if isinstance(loglevel, str):
        loglevel = getattr(logging, loglevel.upper())
    coloredlogs.install(level=loglevel)
    ctx.ensure_object(dict)
    ctx.obj = api

@main.group("module")
@click.pass_context
def _module(ctx):
    ctx.obj = ctx.obj.module

@_module.command("get")
@click.pass_context
@click.option('--arg1')
def _module_get(ctx, **kwargs):
    result = ctx.obj.get(**kwargs)
    print(result)


if __name__ == "__main__":
    main(prog_name="PROGRAM_NAME")  # pylint: disable=no-value-for-parameter # (because it's click decorated)