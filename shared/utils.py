import sys
import os
import importlib
import functools
from types import SimpleNamespace
import logging
from http import HTTPStatus
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

import click
import requests

def validate(data, schema):
    return data

def encode(data, schema):
    return str(data).encode()

def decode(data, schema):
    return data.decode()

def convert(data, schema):
    return data.decode()

def dec(fun):
    @functools.wraps(fun)
    def fun2(*args, **kwargs):
        return fun(*args, **kwargs) + 1
    return fun2

# todo
class WSGIHandler:
    routes = {}
    
    def __init__(self, api):
        self.api = api

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD'].upper()
        path = environ['PATH_INFO']
        query = parse_qs(environ['QUERY_STRING'], strict_parsing=False)
        content_type = environ['CONTENT_TYPE'].lower()
        content_length = int(environ['CONTENT_LENGTH'] or '0')
        authorization = environ.get("HTTP_AUTHORIZATION")
        if authorization:  # <auth-scheme> <authorisation-parameters>
            authorization = authorization.split(" ")
            authorization = (authorization[0].upper(), " ".join(authorization[1:]))
        input = environ["wsgi.input"]

        method_implies_data = method in ("POST", "PATCH", "PUT")
        assert bool(method_implies_data) == bool(content_length)

        
        handler, path_arguments, input_name = self.get_handler(path, method)
        query.update(path_arguments)

        assert bool(input_name) == bool(content_length)

        content_length_actual = None
        if input_name:
            input = environ["wsgi.input"]
            data = input.read(content_length)
            content_length_actual = len(data)
            query[input_name] = data
                
        logging.debug(
            {
                "method": method,
                "path": path,
                "query": query,
                "content_type": content_type,
                "content_length": content_length,
                "content_length_actual": content_length_actual,
                "authorization": authorization
            }
        )

        result = handler(**query) or b''
        
        status = self.get_status_str(200)
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(result)))
        ]
        start_response(status, response_headers)
        return [result]

    def route(self, method, path, path_args=None, input_name=None):
        def register(fun):
            # TODO
            self.routes[None] = fun
            return fun
        return register

    def get_handler(self, path, method):
        # TODO
        handler = self.routes[None]
        path_arguments = {"b": "2"}
        input_name = "data"
        return handler, path_arguments, input_name

    @staticmethod
    def get_status_str(code):
        return '%s %s' % (code, HTTPStatus(code).phrase)


def output(fun):
    def fun2(*args, **kwargs):
        output = fun(*args, **kwargs)
        sys.stdout.buffer.write(output)
    
    return fun2

def input(fun):
    def fun2(ctx, *args, **kwargs):
        input = sys.stdin.buffer.read()
        return fun(ctx, input, *args, **kwargs)
    return fun2

def request(method, url, params=None, data=None):    
    res = requests.request(method, url, params=params, data=data)
    res.raise_for_status()
    return res.content


def import_filepath(filepath, name=None):    
    if not name:
        name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(name, filepath)  
    mod = importlib.util.module_from_spec(spec)    
    spec.loader.exec_module(mod)
    return mod  

def wsgi_serve(wsgi_script):
    
    @click.command()
    @click.option(
        "--loglevel",
        "-l",
        type=click.Choice(["debug", "info", "warning", "error"]),
        default="debug",
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
        wsgi_mod = import_filepath(wsgi_script)
        with make_server('', port, wsgi_mod.application) as server:        
            server.serve_forever()
    
    main()

def get_api(remote=None):
    from api import api as api_local
    from client import api as api_remote
    if remote:        
        api = api_remote(remote)
    else:        
        api = api_local()
    return api

def create_cli_main():    
    @click.group("main")
    @click.option("--remote", "-r")
    @click.pass_context
    def main(ctx, remote):        
        ctx.obj = SimpleNamespace(
            api=get_api(remote)
        )
    
    return main