from http import HTTPStatus
import logging
from urllib.parse import parse_qs
import re

import logging

LOGGING_DATE_FMT = '%Y-%m-%d %H:%M:%S'
LOGGING_FMT = "[%(asctime)s %(levelname)7s] %(message)s"

logging.basicConfig(format=LOGGING_FMT, datefmt=LOGGING_DATE_FMT, level=logging.DEBUG)

import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../1_api')
from api import api

def serve(fun):
    def _fun(*args, **kwargs):
        logging.info('request')
        res = fun(*args, **kwargs)
        logging.info('response')
        return res
    return _fun

handlers = {
    ('GET', '^/module/get$'): serve(api.module.get),
    ('POST', '^/module/post$'): serve(api.module.post),
    
    ('GET', '^/resource/(?P<id>[0-9]+)$'): serve(api.resource.get),
    ('POST', '^/resource$'): serve(api.resource.post),
    ('PUT', '^/resource/(?P<id>[0-9]+)$'): serve(api.resource.put),
    ('PATCH', '^/resource/(?P<id>[0-9]+)$'): serve(api.resource.patch),
    ('DELETE', '^/resource/(?P<id>[0-9]+)$'): serve(api.resource.delete),
    ('GET', '^/resource$'): serve(api.resource.list)    
}


def application(environ, start_response):
    
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    query = parse_qs(environ['QUERY_STRING'], strict_parsing=False)
    content_type = environ['CONTENT_TYPE']
    content_length = int(environ['CONTENT_LENGTH'] or '0')

    selected_handler = None
    for (meth, path_pat), handler in handlers.items():
        if meth == method and re.match(path_pat, path):
            query.update(re.match(path_pat, path).groupdict())
            selected_handler = handler
            break
    
    def get_response(code):
        return '%d %s' % (code.value, code.phrase)

    if not selected_handler:
        start_response(get_response(HTTPStatus.NOT_FOUND), [])
        return []
    
    result = selected_handler(**query)

    result = str(result).encode()

    status = get_response(HTTPStatus.OK)
    response_headers = [('Content-type', 'text/plain'),
                  ('Content-Length', str(len(result)))]
    start_response(status, response_headers)
    return [result]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as server:
        server.serve_forever()