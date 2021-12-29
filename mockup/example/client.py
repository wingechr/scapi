import logging
from types import SimpleNamespace
from urllib.parse import urlencode

import requests

def api(host, **_kwargs):

    logging.debug("loading api: %s", host)

    def request(method, path):
        def _fun(**kwargs):        
            # TODO: check if api has proper data path
            if "data" in kwargs:
                data = kwargs.pop("data")
            else:
                data = b''

            url = host + path % kwargs
            query = urlencode(kwargs)
            logging.debug('client request %s %s', method, url)
            res = requests.request(method=method, url=url, params=query, data=data)
            res.raise_for_status()
            res = res.content
            logging.debug('client response')
            return res
        return _fun


    return SimpleNamespace(
        module=SimpleNamespace(
            submodule=SimpleNamespace(
                get=request("GET", "/module/submodule/get"),
                post=request("POST", "/module/submodule/post")
            )
        ),
        rest=SimpleNamespace(
            resource=SimpleNamespace(
                delete=request("DELETE", "/rest/resource"),
                get=request("GET", "/rest/resource"),
                list=request("GET", "/rest/resource"),
                patch=request("PATCH", "/rest/resource"),
                post=request("POST", "/rest/resource"),
                put=request("PUT", "/rest/resource")
            )
        )
    )