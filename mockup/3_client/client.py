import logging
import requests

LOGGING_DATE_FMT = '%Y-%m-%d %H:%M:%S'
LOGGING_FMT = "[%(asctime)s %(levelname)7s] %(message)s"

logging.basicConfig(format=LOGGING_FMT, datefmt=LOGGING_DATE_FMT, level=logging.DEBUG)

import sys
import re
import os
import inspect
import requests
from urllib.parse import urlencode

def request(method, path):
    def _fun(**kwargs):        
        url = 'http://localhost:8000' + path % kwargs
        query = urlencode(kwargs)
        logging.info('%s %s', method, url)
        res = requests.request(method=method, url=url, params=query)
        res.raise_for_status()
        res = res.content
        logging.info('response')
        return res
    return _fun


from types import SimpleNamespace
api = SimpleNamespace(
module = SimpleNamespace(
    get=request("GET", "/module/get"),
    post=request("POST", "/module/post")
),
resource = SimpleNamespace(
    get=request("GET", "/resource/%(id)s"),
    post=request("POST", "/resource"),
    put=request("PUT", "/resource/%(id)s"),
    patch=request("PATCH", "/resource/%(id)s"),
    list=request("GET", "/resource"),
    delete=request("DELETE", "/resource/%(id)s"),
)
)


