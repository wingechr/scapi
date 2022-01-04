#!/usr/bin/env python3
from collections import OrderedDict
from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from endpoint_api import EndpointApi, Endpoint
from classes import Input, Output


class EndpointClient(EndpointApi):
    """same interface as EndpointApi"""

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
                'def api(remote="http://localhost:8000"):',
                code_main,
                None,
                "return api",
            ),
        )

    @classmethod
    def get_code_source_fun_name(cls, instance):
        return "utils.request"

    @classmethod
    def get_code_fun_body_call_params(cls, instance) -> list:
        params = [("method", '"%s"' % instance.http)]

        if instance.arguments:
            placeholders = ""
            variables = ""
            for a in instance.arguments.values():
                placeholders += "/%s"
                variables += ", " + a.name
            url = '"%s/mod/fun' + placeholders + '" % (remote' + variables + ")"
        else:
            url = '"%s/mod/fun/%s" % remote'
        params.append(("url", url))

        if instance.options:
            params.append(
                (
                    "params",
                    "{"
                    + ",".join(
                        '"%s": %s' % (o.source, o.name)
                        for o in instance.options.values()
                    )
                    + "}",
                )
            )
        if instance.input:
            p = instance.input
            wrap_fun = cls.get_code_wrap_function(instance, p)
            wrap_args = ", " + cls.get_code_wrap_arguments(instance, p)
            line = "%s(%s%s)" % (wrap_fun, p.name, wrap_args)
            params.append(("data", line))
            params.append(("content_type", '"%s"' % instance.input.type.content))

        return ["%s=%s" % p for p in params]

    @classmethod
    def get_code_wrap_function(cls, instance, param):
        if isinstance(param, Input):
            return "utils.encode_content"
        elif isinstance(param, Output):
            return "utils.decode_content"
        else:
            return ""  # requests does the encoding

    @classmethod
    def get_code_wrap_arguments(cls, instance, param):
        if isinstance(param, (Input, Output)):
            content_type = param.type.content
            if content_type:
                return '"%s"' % content_type
            else:
                return "None"
        else:
            return ""  # requests does the encoding
