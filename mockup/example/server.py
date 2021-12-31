from . import utils
import logging
import os

def router():
    pass
        

application = utils.create_wsgi_application(router)

if __name__ == "__main__":
    port = int(os.environ.get("SERVER_PORT", "8000"))
    utils.start_wsgi_server(application, port=port)
