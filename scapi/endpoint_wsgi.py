#!/usr/bin/env python3
from .classes import Argument, Input, Option
from .code import CodeBlock, CommaJoinedCodeBlock, IndentedCodeBlock
from .endpoint import Endpoint
from .endpoint_api import EndpointApi


class EndpointWSGI(Endpoint):
    @classmethod
    def get_signature_parameters(cls, instance):
        params = []
        for p in super().get_signature_parameters(instance):
            if isinstance(p, Input):
                p = p.as_bytes()
            elif isinstance(p, Argument):
                p = p.as_string()
            elif isinstance(p, Option):
                p = p.as_string_array()
            params.append(p)
        return params

    @classmethod
    def get_signature_output(cls, instance):
        if instance.output:
            return instance.output.as_bytes()

    # ---------------------------
    # code generation
    # ---------------------------

    @classmethod
    def get_code(cls):
        return CodeBlock(
            "import logging",
            "import utils",
            None,
            '__version__ = "%s"' % Endpoint.version,
            None,
            "application = utils.WSGIHandler(utils.get_api())",
            None,
            cls.get_code_instances(),
            None,
            IndentedCodeBlock(
                'if __name__ == "__main__":', "utils.wsgi_serve_script(__file__)"
            ),
        )

    @classmethod
    def get_code_group(cls, elements, path):
        return CodeBlock(*elements)

    @classmethod
    def get_code_instance(cls, instance, path):

        output_tgt = EndpointApi.get_signature_output(instance)
        path_args = ['"%s"' % p for p in cls.get_url_path(instance)]
        input_name = '"%s"' % instance.input.name if instance.input else None
        # msut not be empty
        output_content_type = '"%s"' % output_tgt.type.content if output_tgt else "None"
        route = (
            '@application.route("%s", [%s], input_name=%s, output_content_type=%s)'
            % (instance.http, ", ".join(path_args), input_name, output_content_type)
        )

        fun_name = ".".join(["application", "api"] + instance.path)

        parameters_src = cls.get_signature_parameters(instance)
        parameters_tgt = EndpointApi.get_signature_parameters(instance)
        assert len(parameters_src) == len(parameters_tgt)

        param_strs = []
        for pt, ps in zip(parameters_tgt, parameters_src):
            if isinstance(pt, Input):
                param_strs.append(
                    '%s=utils.decode_content(%s, "%s")'
                    % (pt.name, ps.name, pt.type.content)
                )
            elif isinstance(pt, Option):
                if pt.type.multiple:
                    param_strs.append(
                        '%s=utils.list_from_string_list(%s, "%s")'
                        % (pt.name, ps.name, pt.type.type)
                    )
                else:
                    param_strs.append(
                        '%s=utils.single_from_string_list(%s, "%s")'
                        % (pt.name, ps.name, pt.type.type)
                    )
            else:
                param_strs.append(
                    '%s=utils.from_string(%s, "%s")' % (pt.name, ps.name, pt.type.type)
                )

        return CodeBlock(
            route,
            IndentedCodeBlock(
                super().get_code_fun_signature(instance),
                cls.get_code_fun_docstring(instance),
                cls.wrap_function(
                    IndentedCodeBlock(
                        fun_name + "(",
                        CommaJoinedCodeBlock(*param_strs),
                        footer=")",
                    ),
                    output_tgt,
                    "utils.encode_content",
                ),
            ),
            None,
        )

    @classmethod
    def get_code_fun_name(cls, instance):
        return "route_" + instance.name_long

    @classmethod
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s' % instance.description)

        # create URL
        url_pattern = "/".join(cls.get_url_path(instance))

        options = ""  # TODO
        if options:
            options = "?" + options

        result += CodeBlock(
            None,
            IndentedCodeBlock(
                "URL::",  # rst indented literal code
                None,
                "%s %s%s" % (instance.http, url_pattern, options),
                None,
            ),
        )

        result += '"""'
        return result

    @classmethod
    def get_url_path(cls, instance):
        path_args = ["%s" % p for p in instance.path_url]
        path_args += ["(?P<%s>[^/?]+)" % a.name for a in instance.arguments.values()]
        return path_args
