from . import utils
import logging
import os

def router():
    return {
        "get": {
            <__main__.Endpoint object at 0x7f1a860c2358>
        }
        "module": {
            "submodule": {
                "post": {
                    <__main__.Endpoint object at 0x7f1a8414bbe0>
                }
            }
        }
        "rest": {
            "resource": {
                <__main__.Endpoint object at 0x7f1a8414be10>
                ,
                <__main__.Endpoint object at 0x7f1a8414bef0>
                ,
                "^(?<pk>[^/?]+)$": {
                    <__main__.Endpoint object at 0x7f1a84158048>
                    ,
                    <__main__.Endpoint object at 0x7f1a84158198>
                    ,
                    <__main__.Endpoint object at 0x7f1a841582b0>
                    ,
                    <__main__.Endpoint object at 0x7f1a84158400>
                }
            }
        }
    }

application = utils.create_wsgi_application(router)

if __name__ == "__main__":
    port = int(os.environ.get("SERVER_PORT", "8000"))
    utils.start_wsgi_server(application, port=port)
