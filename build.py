#!/usr/bin/env python3

import logging

import os
import click
import coloredlogs

# https://coloredlogs.readthedocs.io/en/latest/api.html#changing-the-date-time-format
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


@click.command()
@click.pass_context
# @click.version_option(__version__)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
)
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def main(ctx, loglevel, schema_json, output_path):
    """Script entry point."""
    if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
        loglevel = getattr(logging, loglevel.upper())
    coloredlogs.install(level=loglevel)
    ctx.ensure_object(dict)


if __name__ == "__main__":
    main(prog_name="python3 build.py")