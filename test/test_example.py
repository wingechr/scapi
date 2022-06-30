import logging
import os
import subprocess as sp
import tempfile
import unittest

import scapi.build

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.DEBUG
)


class TestExample(unittest.TestCase):
    def test_example(self):
        # build example api
        output_dir = tempfile.TemporaryDirectory("scapi")
        logging.debug(f"output_path: {output_dir}")
        example_dir = os.path.join(os.path.dirname(__file__), "example")
        schema_json = os.path.join(example_dir, "example_schema.json")

        # build the api
        scapi.build.build(schema_json, output_dir.name)

        # run unittest of created package
        proc = sp.Popen(["python3", f"{output_dir.name}/test.py"], shell=True)
        proc.communicate()

        self.assertEqual(proc.returncode, 0)

        output_dir.cleanup()
