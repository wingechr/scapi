#!/usr/bin/env python3

import os
from typing import OrderedDict
import click
import shutil
import jsonschema
from build_utils import json_load, text_dump, json_dump
from endpoint import Endpoint
from endpoint_api import EndpointApi
from endpoint_wsgi import EndpointWSGI
from endpoint_client import EndpointClient
from endpoint_cli import EndpointCli
from copy import deepcopy


@click.command()
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def main(schema_json, output_path):

    SRC_DIR = os.path.abspath(os.path.dirname(__file__))

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load(SRC_DIR + "/schema/api.json")
    jsonschema.validate(schema, metaschema)

    # create output directory
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # files from shared
    for name in os.listdir(SRC_DIR + "/shared"):
        if not name.endswith(".py"):
            continue
        shutil.copy(SRC_DIR + "/shared/" + name, output_path + "/" + name)
    # save schema, set metaschema
    json_dump(metaschema, output_path + "/metaschema.json")
    schema_copy = deepcopy(schema)
    schema_copy["$schema"] = "./metaschema.json"
    json_dump(schema_copy, output_path + "/schema.json")

    # create endpoints
    _endpoints = [Endpoint(**ep) for ep in schema["endpoints"]]
    Endpoint.version = schema["version"]

    # generate code for layers
    text_dump(EndpointApi.get_code(), output_path + "/api.py")
    text_dump(EndpointWSGI.get_code(), output_path + "/wsgi.py")
    text_dump(EndpointClient.get_code(), output_path + "/client.py")
    text_dump(EndpointCli.get_code(), output_path + "/cli.py")


if __name__ == "__main__":
    main(prog_name="python3 build.py")
