#!/usr/bin/env python3

import logging
import os
import re
import shutil
import subprocess as sp
from copy import deepcopy

import click
import coloredlogs
import jsonschema

from .endpoint import Endpoint
from .endpoint_api import EndpointApi
from .endpoint_cli import EndpointCli
from .endpoint_client import EndpointClient
from .endpoint_wsgi import EndpointWSGI
from .utils import json_dump, json_load, text_dump

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
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--build-docs", "-d", is_flag=True)
@click.option("--run-test", "-t", is_flag=True)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
)
def main(schema_json, output_path, build_docs, run_test, loglevel):
    if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
        loglevel = getattr(logging, loglevel.upper())
        coloredlogs.install(level=loglevel)

    build(schema_json, output_path, build_docs, run_test)


def build(schema_json, output_path, build_docs=False, run_test=False):

    logging.debug(f"schema_json: {schema_json}")
    logging.debug(f"output_path: {output_path}")

    src_path = os.path.abspath(os.path.dirname(__file__))

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load(src_path + "/schema/api.json")
    jsonschema.validate(schema, metaschema)

    # create output directory
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # files from shared
    shared_path = src_path + "/shared"
    for rt, _ds, fs in os.walk(shared_path):
        for f in fs:
            if re.match(r"^(.*\.py|index.rst|requirements.txt)$", f):
                path = os.path.relpath(rt + "/" + f, shared_path)
                os.makedirs(os.path.dirname(output_path + "/" + path), exist_ok=True)
                shutil.copy(shared_path + "/" + path, output_path + "/" + path)
        #
    # save schema, set metaschema
    os.makedirs(output_path + "/doc/schema", exist_ok=True)
    json_dump(metaschema, output_path + "/doc/schema/metaschema.json")
    schema_copy = deepcopy(schema)
    schema_copy["$schema"] = "./metaschema.json"
    json_dump(schema_copy, output_path + "/doc/schema/schema.json")

    # create endpoints
    for ep in schema["endpoints"]:
        Endpoint(**ep)
    Endpoint.version = schema["version"]

    # generate code for layers
    text_dump(EndpointApi.get_code(), output_path + "/api.py")
    text_dump(EndpointWSGI.get_code(), output_path + "/wsgi.py")
    text_dump(EndpointClient.get_code(), output_path + "/client.py")
    text_dump(EndpointCli.get_code(), output_path + "/main.py")

    if build_docs:
        proc = sp.Popen(
            [
                "sphinx-build",
                output_path + "/doc",
                output_path + "/doc/build",
                "-b",
                "singlehtml",
                "-q",
            ],
            shell=True,
        )
        proc.communicate()
        if proc.returncode:
            logging.error("Building docs failed")

    if run_test:
        proc = sp.Popen(
            ["python3", output_path + "/test.py"],
            shell=True,
        )
        proc.communicate()
        if proc.returncode:
            logging.error("running tests failed")


if __name__ == "__main__":
    main(prog_name="scapi")
