import logging
import re
from http import HTTPStatus
from urllib.parse import parse_qs
import importlib
from wsgiref.simple_server import make_server

import click
import coloredlogs

__version__ = "0.0.0"


def create_handlers(api_module="api"):
    def serve(fun):
        def _fun(*args, **kwargs):
            logging.debug('request')
            res = fun(*args, **kwargs)
            logging.debug('response')
            return res
        return _fun

    api = getattr(importlib.import_module(api_module, package=None), "api")()

    return {
        "^DELETE /rest/resource/(?P<id>[^/?]+)$": serve(api.rest.resource.delete),
        "^GET /module/submodule/get$": serve(api.module.submodule.get),
        "^GET /rest/resource$": serve(api.rest.resource.list),
        "^GET /rest/resource/(?P<id>[^/?]+)$": serve(api.rest.resource.get),
        "^PATCH /rest/resource/(?P<id>[^/?]+)$": serve(api.rest.resource.patch),
        "^POST /module/submodule/post$": serve(api.module.submodule.post),
        "^POST /rest/resource$": serve(api.rest.resource.post),
        "^PUT /rest/resource/(?P<id>[^/?]+)$": serve(api.rest.resource.put)
    }



def application(environ, start_response):
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

    if content_length:
        input = environ["wsgi.input"]
        data = input.read(content_length)
    else:
        data = b''
    
    content_length_actual = len(data)

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

    handlers = create_handlers()

    key = method + ' ' + path
    selected_handler = None
    for pattern, handler in handlers.items():
        match = re.match(pattern, key)
        if match:
            selected_handler = handler
            parameters = match.groupdict()
            query.update(parameters)

    if not selected_handler:
        raise Exception(key)

    def get_status_str(code):
        return str(code.value) + ' ' + code.phrase

    if not selected_handler:
        start_response(get_status_str(HTTPStatus.NOT_FOUND), [])
        return []

    if data: # TODO: check if api requires data input
        result = selected_handler(data, **query)
    else:
        result = selected_handler(**query)

    result = str(result).encode()

    status = get_status_str(HTTPStatus.OK)
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(result)))
    ]
    start_response(status, response_headers)
    return [result]



@click.command()
@click.pass_context
@click.version_option(__version__)
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
def main(ctx, loglevel, port):
    if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
        loglevel = getattr(logging, loglevel.upper())
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
    coloredlogs.install(level=loglevel)
    ctx.ensure_object(dict)
        
    with make_server('', port, application) as server:        
        logging.info("start serving on http://localhost:%d", port)
        server.serve_forever()
    

if __name__ == "__main__":
    main()