#!/usr/bin/env python3
from collections import OrderedDict
from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from endpoint_api import EndpointApi, Endpoint
from endpoint_wsgi import EndpointWSGI
from classes import Input, Output


class EndpointClient(EndpointApi):
    """same interface as EndpointApi"""

    # ------------------------------------
    # code generation
    # ------------------------------------

    @classmethod
    def get_code(cls):
        return CodeBlock(
            "import logging",
            "import utils",
            None,
            '__version__ = "%s"' % Endpoint.version,
            None,
            None,
            IndentedCodeBlock(
                'def api(remote="http://localhost:8000"):',
                cls.get_code_instances(),
                None,
                "return api",
            ),
        )

        # create URL
        url_pattern = "/".join(cls.get_url_path(instance))
        result += CodeBlock(
            None,
        )

    @classmethod
    def get_code_instance(cls, instance, path):

        params = [("method", '"%s"' % instance.http)]

        url = '"%s/' + "/".join(instance.path_url)
        if instance.arguments:
            placeholders = ""
            variables = ""
            for a in instance.arguments.values():
                placeholders += "/%s"
                variables += ", " + a.name
            url += placeholders + '" % (remote' + variables + ")"
        else:
            url += '" % remote'

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
            line = 'utils.encode_content(%s, "%s")' % (
                p.name,
                instance.input.type.content,
            )
            params.append(("data", line))
            params.append(("content_type", '"%s"' % instance.input.type.content))

        params = ["%s=%s" % p for p in params]

        output = cls.get_signature_output(instance)

        return CodeBlock(
            "@staticmethod",
            IndentedCodeBlock(
                super().get_code_fun_signature(instance),
                cls.get_code_fun_docstring(instance),
                cls.wrap_function(
                    IndentedCodeBlock(
                        "utils.request(", CommaJoinedCodeBlock(*params), footer=")"
                    ),
                    output,
                    "utils.decode_content",
                ),
            ),
            None,
        )
