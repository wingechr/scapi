#!/usr/bin/env python3

import logging
import os
import re
import shutil
import subprocess as sp
from copy import deepcopy

import click
import jsonschema

from .build_utils import json_dump, json_load, text_dump
from .endpoint import Endpoint
from .endpoint_api import EndpointApi
from .endpoint_cli import EndpointCli
from .endpoint_client import EndpointClient
from .endpoint_wsgi import EndpointWSGI


@click.command()
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
@click.option("--build-docs", "-d", is_flag=True)
@click.option("--run-test", "-t", is_flag=True)
def main(schema_json, output_path, build_docs, run_test):
    build(schema_json, output_path, build_docs, run_test)


def build(schema_json, output_path, build_docs=False, run_test=False):

    logging.debug(f"schema_json: {schema_json}")
    logging.debug(f"output_path: {output_path}")

    SRC_DIR = os.path.abspath(os.path.dirname(__file__))

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load(SRC_DIR + "/schema/scapi.schema.json")
    jsonschema.validate(schema, metaschema)

    # create output directory
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # files from shared
    shared_path = SRC_DIR + "/shared"
    for rt, _, fs in os.walk(shared_path):
        for f in fs:
            if re.match(r"^.*\.(py|rst)$", f):
                relpath = os.path.relpath(rt + "/" + f, shared_path)
                path = shared_path + "/" + relpath
                path2 = output_path + "/" + relpath
                os.makedirs(os.path.dirname(path2), exist_ok=True)
                shutil.copy(path, path2)
        #
    # save schema, set metaschema
    json_dump(metaschema, output_path + "/metaschema.json")
    schema_copy = deepcopy(schema)
    schema_copy["$schema"] = "./metaschema.json"
    json_dump(schema_copy, output_path + "/schema.json")

    # create endpoints
    for ep in schema["endpoints"]:
        Endpoint(**ep)
    Endpoint.version = schema["version"]

    # generate code for layers
    text_dump(EndpointApi.get_code(), output_path + "/api.py")
    text_dump(EndpointWSGI.get_code(), output_path + "/wsgi.py")
    text_dump(EndpointClient.get_code(), output_path + "/client.py")
    text_dump(EndpointCli.get_code(), output_path + "/cli.py")
    text_dump("", output_path + "/__init__.py")

    if build_docs:
        proc = sp.Popen(
            [
                "sphinx-build",
                output_path + "/doc",
                output_path + "/doc/build",
                "-b",
                "singlehtml",
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
    main(prog_name="python3 build.py")
