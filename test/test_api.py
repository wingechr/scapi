# coding: utf-8
import logging

logging.basicConfig(
    format="[%(asctime)s %(levelname)7s] %(message)s", level=logging.INFO
)

import unittest
import sys
import os

import jsonschema

from utils import json_load


class TestApi(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_validate_metaschema(self):
        schema = json_load("schema/api.json")
        instance = json_load("test/api.json")
        res = jsonschema.validate(instance, schema)
        logging.info(res)
