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
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s' % instance.description)

        # create URL
        url_pattern = "/".join(EndpointWSGI.get_url_path(instance))
        result += CodeBlock(
            None,
            IndentedCodeBlock(
                "URL", None, "%s %s" % (instance.http, url_pattern), None
            ),
        )

        result += '"""'
        return result

    @classmethod
    def get_url_path(cls, instance):
        path_args = ["%s" % p for p in instance.path_url]
        path_args += ["(?P<%s>[^/?]+)" % a.name for a in instance.arguments.values()]
        return path_args

    @classmethod
    def get_code_fun_decorators(cls, instance):
        path_args = ['"%s"' % p for p in cls.get_url_path(instance)]
        input_name = '"%s"' % instance.input.name if instance.input else None
        output_content_type = (
            '"%s"' % instance.output.type.content if instance.output else None
        )

        return CodeBlock(
            '@application.route("%s", [%s], input_name=%s, output_content_type=%s)'
            % (instance.http, ", ".join(path_args), input_name, output_content_type)
        )

    @classmethod
    def get_code_fun_name(cls, instance):
        return "route_" + instance.name_long

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
            content_type = param.type.content
            if content_type:
                return '"%s"' % content_type
            else:
                return "None"
        else:
            return '"%s"' % param.type.type
