import logging
import os
import subprocess as sp
import tempfile
import unittest

import scapi.__main__

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.DEBUG
)


class TestExample(unittest.TestCase):
    def test_example(self):
        # build example api
        with tempfile.TemporaryDirectory("scapi") as output_dir:
            logging.info(f"BUILD PATH: {output_dir}")
            example_dir = os.path.join(os.path.dirname(__file__), "example")
            schema_json = os.path.join(example_dir, "example_schema.json")

            # build the api
            scapi.__main__.build(schema_json, output_dir)

            # run unittest of created package
            logging.info("Testing examples")
            env = os.environ
            env["PYTHONPATH"] = example_dir
            proc = sp.Popen(
                ["python3", f"{output_dir}/test.py"],
                shell=True,
                env=env,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
            _, stderr = proc.communicate()

            self.assertEqual(proc.returncode, 0, stderr.decode())
