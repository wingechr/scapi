# coding: utf-8
import logging
import socket
import threading
import time
import unittest
from functools import partial

import utils
from api import api as api_local
from client import api as api_remote
from wsgi import application

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.DEBUG
)


class TestTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # get free port
        cls.socket = socket.socket()
        cls.socket.bind(("", 0))
        port = cls.socket.getsockname()[1]
        cls.socket.close()
        target = partial(utils.wsgi_serve, port, application)
        server_thread = threading.Thread(target=target, daemon=True)
        server_thread.start()
        time.sleep(1)  # give server a little time to startup
        cls.api_remote = api_remote("http://localhost:%d" % port)
        cls.api_local = api_local()
        cls.schema = utils.load_schema()

    @classmethod
    def tearDownClass(cls):
        # cls.socket.close()
        pass

    def test_examples(self):
        """find all examples and test them"""
        for endpoint in self.schema["endpoints"]:
            path = endpoint["path"]
            callable_remote = self.api_remote
            callable_local = self.api_local
            for p in path:
                callable_remote = getattr(callable_remote, p)
                callable_local = getattr(callable_local, p)

            for example in endpoint.get("examples", []):
                inputs = example["inputs"]
                expected_output = example["output"]

                logging.info(
                    "TESTING local endpoint example: %s(%s) == %s",
                    ".".join(path),
                    inputs,
                    expected_output,
                )
                output_local = callable_local(**inputs)
                self.assertEqual(output_local, expected_output)

                logging.info(
                    "TESTING remote endpoint example: %s(%s) == %s",
                    ".".join(path),
                    inputs,
                    expected_output,
                )
                output_remote = callable_remote(**inputs)
                self.assertEqual(output_remote, expected_output)


if __name__ == "__main__":
    unittest.main()
