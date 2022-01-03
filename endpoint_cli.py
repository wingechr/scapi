#!/usr/bin/env python3

from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from classes import Input, Option, Argument, Output
from endpoint import Endpoint


class EndpointCli(Endpoint):

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
            "main = utils.create_cli_main(__version__)",
            None,
            code_main,
            None,
            IndentedCodeBlock(
                'if __name__ == "__main__":',
                # 'main(prog_name="TODO")'
                "main()",
            ),
        )

    @classmethod
    def get_code_fun_decorators(cls, instance):
        path = ["main"] + instance.path
        group_path, name = path[:-1], path[-1]
        group_name = "_".join(group_path)

        result = CodeBlock()
        result += '@%s.command("%s")' % (group_name, name)
        result += "@utils.click.pass_context"

        for a in instance.arguments.values():
            result += '@utils.click.argument("%s", %s)' % (a.name, a.type.click_repr)
        for o in instance.options.values():
            result += '@utils.click.option("--%s", %s, help="%s")' % (
                o.name,
                o.type.click_repr,
                o.click_help,
            )

        if instance.input:
            result += "@utils.input_stdin"
        if instance.output:
            result += "@utils.output_stdout"

        return result

    @classmethod
    def get_code_fun_name(cls, instance):
        return "main_" + instance.name_long

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
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s"""' % instance.description)
        return result

    @classmethod
    def get_code_source_fun_name(cls, instance):
        return ".".join(["ctx", "obj", "api"] + instance.path)

    @classmethod
    def get_code_fun_def_params(cls, instance) -> list:
        """add ctx as fist arg"""
        result = super().get_code_fun_def_params(instance)
        result.insert(0, "ctx")
        return result

    @classmethod
    def get_code_fun_body_call_params(cls, instance) -> list:
        return super().get_code_fun_body_call_params(instance, use_source=False)

    @classmethod
    def get_code_params(cls, instance):
        params = []
        for p in super().get_code_params(instance):
            # if isinstance(p, Input):
            #    p = p.get_modified(type={"type": "bytes"})
            params.append(p)
        return params

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
        else:
            return ""  # click already converts

    @classmethod
    def get_code_wrap_arguments(cls, instance, param):
        if isinstance(param, (Input, Output)):
            schema = param.type.content_params.get("schema")
            if schema:
                return '"%s"' % schema
            else:
                return "None"
        else:
            return ""  # click already converts
