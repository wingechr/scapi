#!/usr/bin/env python3

from .classes import Argument, Input, Option
from .code import CodeBlock, CommaJoinedCodeBlock, IndentedCodeBlock
from .endpoint import Endpoint
from .endpoint_api import EndpointApi


class EndpointWSGI(Endpoint):
    @classmethod
    def get_signature_options(cls, instance):
        params = []
        for p in super().get_signature_parameters(instance):
            if isinstance(p, Option):
                params.append(p)
        return params

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

        # create docs for all endpoints using sphinxcontrib-httpdomain
        # https://sphinxcontrib-httpdomain.readthedocs.io/en/stable/

        endpoint_docs = []
        for ep in cls._instances:
            # /users/(int:user_id)/posts/(tag)

            options_docs = []
            for op in cls.get_signature_options(ep):
                options_docs.append(
                    f":query {op.type.url_type} {op.name}: {op.description}"
                )

            url = cls.get_url_doc(ep)

            endpoint_docs.append(
                IndentedCodeBlock(
                    f".. http:{ep.http}:: /{url}",
                    None,
                    ep.description,
                    None,
                    options_docs,
                    """
                :reqheader Authorization: optional token to authenticate
                :resheader X-Messages: TODO: server messages
                :statuscode 200: OK
                """,
                    None,
                )
            )

        docstring = CodeBlock('"""', endpoint_docs, '"""')

        return CodeBlock(
            docstring,
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
        return None

    @classmethod
    def get_url_path(cls, instance):
        path_args = ["%s" % p for p in instance.path_url]
        path_args += ["(?P<%s>[^/?]+)" % a.name for a in instance.arguments.values()]
        return path_args

    @classmethod
    def get_url_doc(cls, instance):
        path_args = ["%s" % p for p in instance.path_url]
        path_args += [
            f"({a.type.url_type}:{a.name})" for a in instance.arguments.values()
        ]
        path_args = "/".join(path_args)
        return path_args
