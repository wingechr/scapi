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
    def get_code(cls):
        return CodeBlock(
            "import logging",
            "import utils",
            None,
            '__version__ = "%s"' % Endpoint.version,
            None,
            None,
            "# imports of external code",
            *["import %s" % i for i in cls.get_imports()],  # imports used by base code
            IndentedCodeBlock(cls.get_code_instances())
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
    def get_code_instance(cls, instance, path):

        fun_name = ".".join(instance.source.imports + instance.source.path)
        parameters_src = cls.get_signature_parameters(instance)
        output = cls.get_signature_output(instance)

        param_strs = []
        for p in parameters_src:
            if isinstance(p, Input):
                param_strs.append(
                    '%s=%s(%s, "%s")'
                    % (p.source, "utils.validate_content", p.name, p.type.content)
                )
            else:
                param_strs.append(
                    "%s=%s(%s, %s)"
                    % (
                        p.source,
                        "utils.validate",
                        p.name,
                        p.type.python_type_validation,
                    )
                )

        return CodeBlock(
            "@staticmethod",
            IndentedCodeBlock(
                super().get_code_fun_signature(instance),
                cls.get_code_fun_docstring(instance),
                cls.wrap_function(
                    IndentedCodeBlock(
                        fun_name + "(",
                        CommaJoinedCodeBlock(*param_strs),
                        footer=")",
                    ),
                    output,
                    "utils.validate_content",
                ),
            ),
            None,
        )

    @classmethod
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s' % instance.description)
        params = cls.get_signature_parameters(instance)
        output = cls.get_signature_output(instance)

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
