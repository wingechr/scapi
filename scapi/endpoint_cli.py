#!/usr/bin/env python3

from .classes import Argument, InputData
from .code import CodeBlock, CommaJoinedCodeBlock, IndentedCodeBlock
from .endpoint import Endpoint
from .endpoint_api import EndpointApi


class EndpointCli(Endpoint):
    @classmethod
    def get_signature_parameters(cls, instance):
        params = [
            Argument(name="ctx", type={"type": "object"}, description="click context")
        ]
        for p in super().get_signature_parameters(instance):
            if isinstance(p, InputData):
                p = p.as_bytes()
            params.append(p)
        return params

    @classmethod
    def get_signature_output(cls, instance):
        if instance.parameters.output_data:
            return instance.parameters.output_data.as_bytes()

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
            "main = utils.create_cli_main(__version__)",
            None,
            cls.get_code_instances(),
            None,
            IndentedCodeBlock(
                'if __name__ == "__main__":',
                # 'main(prog_name="TODO")'
                "main()",
            ),
        )

    @classmethod
    def get_code_group(cls, elements, path):
        """create nested click groups"""
        if path:
            path = ["main"] + path
            group_path, name = path[:-1], path[-1]
            supergroup_name = "_".join(group_path)
            group_name = "_".join(path)

            return CodeBlock(
                CodeBlock(
                    None,
                    '@%s.group("%s")' % (supergroup_name, name),
                    "@utils.click.pass_context",
                    IndentedCodeBlock("def %s(ctx):" % group_name, "pass"),
                    None,
                ),
                CodeBlock(*elements),
            )
        else:
            return CodeBlock(*elements)

    @classmethod
    def get_code_instance(cls, instance, path):

        # create decorators
        path = ["main"] + instance.path
        group_path, name = path[:-1], path[-1]
        group_name = "_".join(group_path)
        decorators = CodeBlock()
        decorators += '@%s.command("%s")' % (group_name, name)
        decorators += "@utils.click.pass_context"
        for o in instance.parameters.arguments.values():
            decorators += '@utils.click.option("--%s", %s, help="%s")' % (
                o.name_target,
                o.type.click_repr,
                o.click_help,
            )
        if instance.parameters.input_data:
            decorators += "@utils.InputData_stdin"
        if instance.parameters.output_data:
            decorators += "@utils.output_stdout"

        fun_name = ".".join(["ctx", "obj", "api"] + instance.path)
        parameters_src = cls.get_signature_parameters(instance)
        parameters_src = parameters_src[1:]  # remove ctx
        parameters_tgt = EndpointApi.get_signature_parameters(instance)
        assert len(parameters_src) == len(parameters_tgt)

        param_strs = []
        for pt, ps in zip(parameters_tgt, parameters_src):
            if isinstance(pt, InputData):
                param_strs.append(
                    '%s=utils.decode_content(%s, "%s")'
                    % (pt.name_target, ps.name_target, pt.type.content)
                )
            else:
                param_strs.append("%s=%s" % (pt.name_target, ps.name_target))

        output_tgt = EndpointApi.get_signature_output(instance)

        return CodeBlock(
            decorators,
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
        return "main_" + instance.name_long

    @classmethod
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s"""' % instance.description)
        return result
