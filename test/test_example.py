import logging
import os
import subprocess as sp
import tempfile
import unittest

import scapi.build

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.INFO
)


class TestExample(unittest.TestCase):
    def test_example(self):
        # build example api
        with tempfile.TemporaryDirectory("scapi") as output_dir:
            logging.debug(f"output_path: {output_dir}")
            example_dir = os.path.join(os.path.dirname(__file__), "example")
            schema_json = os.path.join(example_dir, "example_schema.json")

            # build the api
            scapi.build.build(schema_json, output_dir)

            # run unittest of created package
            env = os.environ
            env["PYTHONPATH"] = example_dir
            proc = sp.Popen(
                ["python3", f"{output_dir}/test.py"],
                shell=True,
                env=env,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
            proc.communicate()

            self.assertEqual(proc.returncode, 0)
