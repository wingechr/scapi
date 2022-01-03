#!/usr/bin/env python3

from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from endpoint import Endpoint
from classes import Input, Output


class EndpointApi(Endpoint):
    @classmethod
    def get_imports(cls):
        imports = set()
        for ep in cls._instances:
            imports.add(tuple(ep.source.imports))
        return [".".join(x) for x in sorted(imports)]

    # ------------------------------------
    # code generation
    # ------------------------------------

    @classmethod
    def get_code_main_wrapper(cls, code_main):
        return CodeBlock(
            "import logging",
            "import utils",
            None,
            '__version__ = "%s"' % Endpoint.version,
            None,
            None,
            IndentedCodeBlock(
                "def api():",
                None,
                *[
                    "import %s" % i for i in cls.get_imports()
                ],  # imports used by base code
                code_main,
                None,
                "return api"
            ),
        )

    @classmethod
    def get_code_group(cls, elements, path):
        """nest endpoints in classes"""
        if path:
            name = path[-1]
        else:
            name = "api"
        return CodeBlock(None, IndentedCodeBlock("class %s:" % name, *elements))

    @classmethod
    def get_code_fun_decorators(cls, instance):
        return CodeBlock("@staticmethod")

    @classmethod
    def get_code_wrap_function(cls, instance, param):
        if isinstance(param, (Input, Output)):
            return "utils.validate_content"
        else:
            return "utils.validate"

    @classmethod
    def get_code_wrap_arguments(cls, instance, param):
        if isinstance(param, (Input, Output)):
            schema = param.type.content_params.get("schema")
            if schema:
                return '"%s"' % schema
            else:
                return "None"
        else:
            return '"%s"' % param.type.type
