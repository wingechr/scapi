import functools
import importlib
import json
import logging
import os
import re
import sys
from http import HTTPStatus
from types import SimpleNamespace
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

import click
import coloredlogs
import jsonschema
import requests

BASE_DIR = os.path.dirname(__file__)
SCHEMA_DIR = BASE_DIR + "/doc/schema"

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


def load_schema():
    with open(SCHEMA_DIR + "/schema.json", encoding="utf-8") as file:
        schema = json.load(file)
    return schema


def validate(data, schema):
    # TODO: allow None always?
    # TODO: give argument name on error
    if data is not None:
        # TODO: CLI returns tuple instead of list
        # which fails validation
        if isinstance(data, tuple):
            data = list(data)
        jsonschema.validate(data, schema)
    return data


def parse_content_type(content_type):
    result = dict()
    content_type = content_type or ""
    for idx, part in enumerate(content_type.split(";")):
        if idx == 0:
            key, name = "type", part
        else:
            key, name = part.split("=")
        result[key.strip().lower()] = name.strip()
    return result


def validate_content(data, content_type):
    # TODO: don't use content_type
    # but only validate if we have a datapackage.resource schema
    content_type = parse_content_type(content_type)
    if content_type["type"] == "application/octet-stream":
        assert type(data) == bytes
    elif content_type["type"] == "application/json":
        pass
        # schema = content_type.get("schema")
        # TODO: validate schema using frictionless?:
        # where are resource schemata stored??
    else:
        logging.error("NOT IMPLEMENTED: %s", content_type["type"])
    return data


def encode_content(data, content_type):
    # TODO: we don't need schema part of content_type
    content_type = parse_content_type(content_type)
    if content_type["type"] == "application/octet-stream":
        return data
    elif content_type["type"] == "application/json":
        encoding = content_type.get("charset", "utf-8").lower()
        # if not utf-8: better ensure ascii
        ensure_ascii = not encoding.startswith("utf")
        return json.dumps(data, ensure_ascii=ensure_ascii).encode(encoding=encoding)
    else:
        logging.error("NOT IMPLEMENTED: %s", content_type["type"])


def decode_content(data, content_type):
    # TODO: we don't need schema part of content_type
    content_type = parse_content_type(content_type)
    if content_type["type"] == "application/octet-stream":
        return data
    elif content_type["type"] == "application/json":
        encoding = content_type.get("charset", "utf-8").lower()
        return json.loads(data.decode(encoding=encoding))
    else:
        logging.error("NOT IMPLEMENTED: %s", content_type["type"])


def list_from_string_list(data, type):
    if not data:
        result = []
    else:
        result = [from_string(s, type) for s in data]
    return result


def single_from_string_list(data, type):
    if not data:
        result = None
    else:
        assert len(data) == 1
        result = from_string(data[0], type)
    return result


def from_string(data, type):
    if type == "integer":
        result = click.types.INT.convert(data, None, None)
    elif type == "number":
        result = click.types.FLOAT.convert(data, None, None)
    elif type == "boolean":
        result = click.types.BOOL.convert(data, None, None)
    else:
        result = data
    return result


class WSGIHandler:
    routes = {
        "GET": {"routes": {}},
        "POST": {"routes": {}},
        "PATCH": {"routes": {}},
        "DELETE": {"routes": {}},
        "PUT": {"routes": {}},
    }

    def __init__(self, api):
        self.api = api
        logging.debug("Connect handler to api")

    def __call__(self, environ, start_response):
        method = environ["REQUEST_METHOD"].upper()
        path = environ["PATH_INFO"].lstrip("/").split("/")
        query = parse_qs(environ["QUERY_STRING"], strict_parsing=False)
        content_type = environ["CONTENT_TYPE"].lower()
        content_length = int(environ["CONTENT_LENGTH"] or "0")
        authorization = environ.get("HTTP_AUTHORIZATION")

        request_messages = environ.get("HTTP_MESSAGES")
        if request_messages:
            request_messages = json.loads(request_messages)

        if authorization:  # <auth-scheme> <authorisation-parameters>
            token = re.match(
                "^Token:? +(?P<token>[^ ]+)$", authorization, re.IGNORECASE
            ).group(1)
        else:
            token = None

        input = environ["wsgi.input"]

        logging.debug(
            {
                "method": method,
                "path": path,
                "query": query,
                "content_type": content_type,
                "content_length": content_length,
                "token": token,
            }
        )

        # todo: compare content_type with expected content_type?

        method_implies_data = method in ("POST", "PATCH", "PUT")
        assert bool(method_implies_data) == bool(content_length)

        handler, path_arguments, attributes = self.get_handler(path, method)
        query.update(path_arguments)
        input_name = attributes.get("input_name")

        assert bool(input_name) == bool(content_length)

        # content_length_actual = None
        if input_name:
            input = environ["wsgi.input"]
            data = input.read(content_length)
            # content_length_actual = len(data)
            query[input_name] = data

        result = handler(**query) or b""
        content_length_result = len(result)

        # TODO get other success codes
        status = self.get_status_str(200)
        output_content_type = attributes.get("output_content_type")

        assert bool(output_content_type) == bool(content_length_result)

        response_messages = [{"level": "DEBUG", "data": "test"}]

        response_headers = []
        if output_content_type:
            response_headers += [
                ("Content-type", output_content_type),
                ("Content-Length", str(content_length_result)),
            ]

        response_headers.append(
            ("Messages", json.dumps(response_messages, ensure_ascii=True))
        )

        start_response(status, response_headers)
        return [result]

    def route(self, method, path, **attributes):
        def register(handler):
            logging.info("register %s %s", method, path)
            tree = self.routes[method]
            for p in path:
                p = re.compile("^" + p + "$")
                if p not in tree["routes"]:
                    tree["routes"][p] = {"routes": {}}
                tree = tree["routes"][p]

            # TODO: why is this getting triggered?
            # if tree.get("handler"):
            #    raise Exception((method, path, tree))

            tree["handler"] = handler
            tree["attributes"] = attributes

            return handler

        return register

    def get_handler(self, path, method):
        path_arguments = {}

        logging.info("getting handler %s %s", method, path)
        tree = self.routes[method]
        for p in path:
            match = None
            for pat, route in tree["routes"].items():
                match = pat.match(p)
                logging.debug("%s, %s, %s", pat, p, match)
                tree = route
                break
            if not match:
                raise Exception((method, path))
            path_arguments.update(match.groupdict())
        handler = tree["handler"]
        attributes = tree["attributes"]

        return handler, path_arguments, attributes

    @staticmethod
    def get_status_str(code):
        return "%s %s" % (code, HTTPStatus(code).phrase)


def output_stdout(fun):
    @functools.wraps(fun)
    def decorated_function(*args, **kwargs):
        output = fun(*args, **kwargs)
        sys.stdout.buffer.write(output)

    return decorated_function


def input_stdin(fun):
    @functools.wraps(fun)
    def decorated_function(ctx, *args, **kwargs):
        input = sys.stdin.buffer.read()
        return fun(ctx, input, *args, **kwargs)

    return decorated_function


def request(method, url, params=None, data=None, content_type=None):
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type

    request_messages = []
    headers["Messages"] = json.dumps(request_messages, ensure_ascii=True)

    res = requests.request(method, url, params=params, data=data, headers=headers)
    # todo compare expected with recieved content type?

    # content_type_resp = res.headers.get("content-type")
    response_messages = res.headers.get("messages")
    if response_messages:
        response_messages = json.loads(response_messages)
        logging.debug("CLIENT RECEIVED MESSAGES %s", response_messages)

    res.raise_for_status()

    return res.content


def import_filepath(filepath, name=None):
    if not name:
        name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def wsgi_serve(port, application):
    with make_server("", port, application) as server:
        logging.info("Serving on port %d", port)
        server.serve_forever()


def wsgi_serve_script(script_file):
    @click.command()
    @click.option(
        "--loglevel",
        "-l",
        type=click.Choice(["debug", "info", "warning", "error"]),
        default="info",
    )
    @click.option(
        "--port",
        "-p",
        type=click.INT,
        default=8000,
    )
    def main(loglevel, port):
        if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
            loglevel = getattr(logging, loglevel.upper())
            coloredlogs.install(level=loglevel)

        logging.error("loading wsgi script from %s", script_file)
        wsgi_mod = import_filepath(script_file)
        application = wsgi_mod.application

        wsgi_serve(port, application)

    main()


def get_api(remote=None):

    if remote:
        import client

        api = client.api(remote)
    else:
        import api

    return api


def create_cli_main(version):

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

    @click.group("main")
    @click.pass_context
    @click.version_option(version)
    @click.option(
        "--loglevel",
        "-l",
        type=click.Choice(["debug", "info", "warning", "error"]),
        default="info",
    )
    @click.option("--remote", "-r", help="Example: http://localhost:8000")
    @click.option("--token", "-t", help="Authorization token")
    def main(ctx, loglevel, remote, token):
        if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
            loglevel = getattr(logging, loglevel.upper())
        coloredlogs.install(level=loglevel)
        ctx.obj = SimpleNamespace(api=get_api(remote), token=token)

    return main
