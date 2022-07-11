#!/usr/bin/env python3
from .code import CodeBlock, CommaJoinedCodeBlock, IndentedCodeBlock
from .endpoint_api import Endpoint, EndpointApi


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

    @classmethod
    def get_code_instance(cls, instance, path):

        params = [("method", '"%s"' % instance.http)]

        url = '"%s/' + "/".join(instance.path_url)
        if instance.parameters.arguments.values():
            placeholders = ""
            variables = ""
            for a in instance.parameters.arguments.values():
                placeholders += "/%s"
                variables += ", " + a.name
            url += placeholders + '" % (remote' + variables + ")"
        else:
            url += '" % remote'

        params.append(("url", url))

        if instance.parameters.input_data:
            p = instance.parameters.input_data
            line = 'utils.encode_content(%s, "%s")' % (
                p.name,
                instance.parameters.input_data.type.content,
            )
            params.append(("data", line))
            params.append(
                ("content_type", '"%s"' % instance.parameters.input_data.type.content)
            )

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
