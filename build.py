#!/usr/bin/env python3

import logging
import os

import click
import coloredlogs
import jsonschema

from utils import json_load


# https://coloredlogs.readthedocs.io/en/latest/api.html#changing-the-date-time-format
coloredlogs.DEFAULT_LOG_FORMAT = "[%(asctime)s %(levelname)7s] %(message)s"
coloredlogs.DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
coloredlogs.DEFAULT_FIELD_STYLES = {
    "asctime": {"color": "black", "bold": True},  # gray
    "levelname": {"color": "black", "bold": True},  # gray
}
coloredlogs.DEFAULT_LEVEL_STYLES = {
    "debug": {"color": "black", "bold": True},  # gray
    "info": {"color": "white"},
    "warning": {"color": "yellow"},
    "error": {"color": "red", "bold": 10},
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

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load("schema/api.json")
    jsonschema.validate(schema, metaschema)

    # collect graph endpoints
    def iter_endpoints(node, parent_data=None):
        node_data = dict((k, v) for k, v in node.items() if k != "children")
        if parent_data is None:  # root node
            path_data = []
        else:
            path_data = parent_data + [node_data]

        if "children" in node:
            for child in node.get("children", []):
                for ep in iter_endpoints(child, path_data):
                    yield ep
        else:
            yield path_data

    endpoints = list(iter_endpoints(schema))

    def create_http_endpoint(ep_path):
        parts = []
        for part in ep_path:
            if "path" in part:
                parts.append(part["path"])
            elif "argument" in part:
                arg_pattern = "%(" + part["argument"] + ")s"
                parts.append(arg_pattern)
            if "method" in part:
                method = part["method"].upper()
                url = "/" + "/".join(parts)

                if part.get("arguments"):
                    args = list(part["arguments"])
                    arg_patterns = [a + "=%(" + a + ")s" for a in args]
                    query = "?" + "&".join(arg_patterns)
                else:
                    query = None

                return (method, url, query)

    def create_code_endpoint(ep_path):
        parts = []
        arguments = []
        for part in ep_path:
            if "path" in part:
                parts.append(part["path"])
            elif "argument" in part:
                arguments.append(part["argument"])
            if "method" in part:
                if part["method"] in ["post", "put", "patch"]:
                    arguments.append("data")
                for arg in part.get("arguments", {}):
                    arguments.append(arg)
                if "path" not in part:
                    if "argument" not in part and part["method"] == "get":
                        parts.append("list")
                    else:
                        parts.append(part["method"])

                if part.get("hasAuthentication", False):
                    arguments.append("token")

                path = ".".join(parts)
                return (path, arguments)

    http_endpoints_set = set()
    code_endpoints_set = set()

    for ep in endpoints:
        path, arguments, query = create_http_endpoint(ep)
        ep_key = (path, arguments)
        if ep_key in http_endpoints_set:
            raise Exception("Duplicate http endpoint: %s" % ep_key)
        http_endpoints_set.add(ep_key)
        http_ep = "%s %s%s" % (path, arguments, query or "")

        path, arguments = create_code_endpoint(ep)
        ep_key = path
        if ep_key in code_endpoints_set:
            raise Exception("Duplicate code endpoint: %s" % ep_key)
        code_endpoints_set.add(ep_key)
        code_ep = "%s(%s)" % (path, ", ".join(arguments))

        print(http_ep, " ==> ", code_ep)


if __name__ == "__main__":
    main(prog_name="python3 build.py")
