import logging
import os
import subprocess as sp
import tempfile
import unittest

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.DEBUG
)


class TestExample(unittest.TestCase):
    def test_example2(self):
        # build example api
        with tempfile.TemporaryDirectory("scapi") as output_dir:
            logging.info(f"BUILD PATH: {output_dir}")
            testdir = os.path.dirname(__file__)
            example_dir = os.path.join(testdir, "example")
            schema_json = os.path.join(example_dir, "example_schema.json")
            env = os.environ
            env["PYTHONPATH"] = example_dir
            cmd = [
                "python3",
                "-m",
                "scapi",
                "--loglevel",
                "debug",
                "--build-docs",
                "--run-test",
                schema_json,
                output_dir,
            ]
            logging.error(" ".join(cmd))
            proc = sp.Popen(
                cmd,
                shell=True,
                env=env,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
            )
            stdout, stderr = proc.communicate()
            stderr = stderr.decode()
            stdout = stdout.decode()
            logging.info(stderr)
            self.assertEqual(proc.returncode, 0, stderr)
