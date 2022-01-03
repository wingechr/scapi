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
    


@main.group("module")
@click.pass_context
def main_module(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "module")


@main_module.group("submodule")
@click.pass_context
def main_module_submodule(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "submodule")


@main_module_submodule.command("get")
@click.pass_context
@click.option("--arg1", help="None")
@click.option("--arg2", help="None")
def main_module_submodule_get(ctx,arg1,arg2):
    ctx.obj["api"] = getattr(ctx.obj["api"], "get")
    result = ctx.obj["api"](arg1=arg1, arg2=arg2)
    ctx.obj["stdout"].write(str(result).encode())


@main_module_submodule.command("post")
@click.pass_context
@click.option("--arg3", help="blabla text arg3")
@click.option("--arg4", help="None")
def main_module_submodule_post(ctx,arg3,arg4):
    ctx.obj["api"] = getattr(ctx.obj["api"], "post")
    data = ctx.obj["stdin"].read()
    result = ctx.obj["api"](data=data, arg3=arg3, arg4=arg4)
    ctx.obj["stdout"].write(str(result).encode())


@main.group("rest")
@click.pass_context
def main_rest(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "rest")


@main_rest.group("resource")
@click.pass_context
def main_rest_resource(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "resource")


@main_rest_resource.command("list")
@click.pass_context
def main_rest_resource_list(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "list")
    result = ctx.obj["api"]()
    ctx.obj["stdout"].write(str(result).encode())


@main_rest_resource.command("post")
@click.pass_context
def main_rest_resource_post(ctx):
    ctx.obj["api"] = getattr(ctx.obj["api"], "post")
    data = ctx.obj["stdin"].read()
    result = ctx.obj["api"](data=data)
    ctx.obj["stdout"].write(str(result).encode())


@main_rest_resource.command("get")
@click.pass_context
@click.argument("id")
def main_rest_resource_get(ctx,id):
    ctx.obj["api"] = getattr(ctx.obj["api"], "get")
    result = ctx.obj["api"](id=id)
    ctx.obj["stdout"].write(str(result).encode())


@main_rest_resource.command("delete")
@click.pass_context
@click.argument("id")
def main_rest_resource_delete(ctx,id):
    ctx.obj["api"] = getattr(ctx.obj["api"], "delete")
    ctx.obj["api"](id=id)


@main_rest_resource.command("put")
@click.pass_context
@click.argument("id")
def main_rest_resource_put(ctx,id):
    ctx.obj["api"] = getattr(ctx.obj["api"], "put")
    data = ctx.obj["stdin"].read()
    ctx.obj["api"](data=data, id=id)


@main_rest_resource.command("patch")
@click.pass_context
@click.argument("id")
def main_rest_resource_patch(ctx,id):
    ctx.obj["api"] = getattr(ctx.obj["api"], "patch")
    data = ctx.obj["stdin"].read()
    ctx.obj["api"](data=data, id=id)



if __name__ == "__main__":
    main(prog_name="PROGRAM_NAME")