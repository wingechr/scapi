#!/usr/bin/env python3
import os
from typing import OrderedDict
import click
import shutil
import jsonschema
from utils import json_load, text_dump
from endpoint import Endpoint, EndpointApi, EndpointServer, EndpointClient, EndpointCli




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

    # copy schema + files from shared
    for name in os.listdir(SRC_DIR + '/shared'):
        if not name.endswith('.py'):
            continue
        shutil.copy(SRC_DIR + '/shared/' + name, output_path + '/' + name)
    shutil.copy(schema_json, output_path + '/schema.json')
    
    # create endpoints
    _endpoints = [Endpoint(**ep) for ep in schema["endpoints"]]

    # generate code for layers
    text_dump(EndpointApi.get_code(), output_path + '/api.py')
    text_dump(EndpointServer.get_code(), output_path + '/server.py')
    text_dump(EndpointClient.get_code(), output_path + '/client.py')
    text_dump(EndpointCli.get_code(), output_path + '/cli.py')

    
if __name__ == "__main__":
    main(prog_name="python3 build.py")
