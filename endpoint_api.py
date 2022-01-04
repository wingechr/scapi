#!/usr/bin/env python3

from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from endpoint import Endpoint
from endpoint_wsgi import EndpointWSGI
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
            "# imports of external code",
            *["import %s" % i for i in cls.get_imports()],  # imports used by base code
            code_main
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
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s' % instance.description)
        params = cls.get_code_params(instance)
        output = cls.get_code_output(instance)

        if params:
            result += None
            result += IndentedCodeBlock(
                "Args:", *[p.get_code_docstring() for p in params]
            )
        if output:
            result += None
            result += IndentedCodeBlock("Returns:", output.get_code_docstring())

        result += '"""'
        return result

    @classmethod
    def get_code_wrap_arguments(cls, instance, param):
        if isinstance(param, (Input, Output)):
            content_type = param.type.content
            if content_type:
                return '"%s"' % content_type
            else:
                return "None"
        else:
            return param.type.python_type_validation
