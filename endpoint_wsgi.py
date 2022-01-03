#!/usr/bin/env python3
from copy import deepcopy
from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from endpoint import Endpoint
from classes import Option, Output, Input, Argument, Type


class EndpointWSGI(Endpoint):
    # ---------------------------
    # code generation
    # ---------------------------

    @classmethod
    def get_code_main_wrapper(cls, code_main):
        return CodeBlock(
            "import logging",
            "import utils",
            None,
            '__version__ = "%s"' % Endpoint.version,
            None,
            "application = utils.WSGIHandler(utils.get_api())",
            None,
            code_main,
            None,
            IndentedCodeBlock(
                'if __name__ == "__main__":', "utils.wsgi_serve(__file__)"
            ),
        )

    @classmethod
    def get_code_fun_decorators(cls, instance):
        path_args = ['"%s"' % p for p in instance.path_url]
        path_args += ['"(?P<%s>.+)"' % a.name for a in instance.arguments.values()]
        input_str = '"%s"' % instance.input.name if instance.input else "None"
        return CodeBlock(
            '@application.route("%s", [%s], %s)'
            % (instance.http, ", ".join(path_args), input_str)
        )

    @classmethod
    def get_code_fun_name(cls, instance):
        return "route_" + instance.name_long

    @classmethod
    def get_code_fun_docstring(cls, instance):
        return CodeBlock()

    @classmethod
    def get_code_source_fun_name(cls, instance):
        return ".".join(["application", "api"] + instance.path)

    @classmethod
    def get_code_params(cls, instance):
        params = []
        for p in super().get_code_params(instance):
            # if isinstance(p, Input):
            #    p = p.get_modified(type={"type": "bytes"})
            # elif isinstance(p, Argument):
            #    p = p.get_modified(type={"type": "string"})
            # elif isinstance(p, Option):
            #    p = p.get_modified(type={"type": "string", "multiple": True})
            params.append(p)
        return params

    @classmethod
    def get_code_fun_body_call_params(cls, instance) -> list:
        return super().get_code_fun_body_call_params(instance, use_source=False)

    @classmethod
    def get_code_output(cls, instance):
        output = instance.output
        if not output:
            return None
        # output = instance.output.get_modified(type={"type": "bytes"})
        return output

    @classmethod
    def get_code_wrap_function(cls, instance, param):
        if isinstance(param, Input):
            return "utils.decode_content"
        elif isinstance(param, Output):
            return "utils.encode_content"
        elif isinstance(param, Option):
            if param.type.multiple:
                return "utils.list_from_string_list"
            else:
                return "utils.single_from_string_list"
        else:
            return "utils.from_string"

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
