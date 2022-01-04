#!/usr/bin/env python3
from collections import OrderedDict
from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from build_utils import add_into_tree, iter_tree
from classes import Source, Argument, Option, Input, Output


class Endpoint:

    _tree = OrderedDict()
    _instances = []

    def __init__(
        self,
        path,
        source,
        arguments=None,
        options=None,
        input=None,
        output=None,
        http=None,
        description=None,
        examples=None,
        authorization=None,
    ):
        self.description = description
        self.path = path
        self._http = http
        self.source = Source(**source)
        self.arguments = OrderedDict(
            (a["name"], Argument(**a)) for a in arguments or []
        )
        self.options = OrderedDict((o["name"], Option(**o)) for o in options or [])
        self.input = Input(**input) if input is not None else None
        self.output = Output(**output) if output is not None else None
        self.authorization = authorization

        add_into_tree(self._tree, self, self.path)
        self._instances.append(self)

    @property
    def name_short(self):
        return self.path[-1]

    @property
    def name_long(self):
        return "_".join(self.path)

    @property
    def http(self):
        if self._http:
            return self._http
        elif self.input:
            return "POST"
        else:
            return "GET"

    @property
    def path_url(self):
        if self._http:
            path = self.path[:-1]
        else:
            path = self.path[:]
        return path

    # ---------------------------
    # code generation
    # ---------------------------

    @classmethod
    def get_code(cls):
        return cls.get_code_main_wrapper(cls.get_code_instances())

    @classmethod
    def get_code_main_wrapper(cls, code_main):
        return code_main

    @classmethod
    def get_code_instances(cls, path=None):
        return iter_tree(
            cls._tree, cls.get_code_group, cls.get_code_instance, path=path
        )

    @classmethod
    def get_code_group(cls, elements, path):
        return CodeBlock(*elements)

    @classmethod
    def get_code_instance(cls, instance, path):
        return CodeBlock(
            None,
            IndentedCodeBlock(
                CodeBlock(
                    cls.get_code_fun_decorators(instance),
                    cls.get_code_fun_signature(instance),
                ),
                cls.get_code_fun_docstring(instance),
                cls.get_code_fun_body(instance),
            ),
        )

    @classmethod
    def get_code_fun_decorators(cls, instance):
        return CodeBlock()

    @classmethod
    def get_code_fun_name(cls, instance):
        return instance.name_short

    @classmethod
    def get_code_fun_signature(cls, instance):
        return "def %s(%s) -> %s:" % (
            cls.get_code_fun_name(instance),
            ", ".join(cls.get_code_fun_def_params(instance)),
            cls.get_code_fun_annotation(instance),
        )

    @classmethod
    def get_code_fun_docstring(cls, instance):
        return CodeBlock('"""%s"""' % instance.description)

    @classmethod
    def get_code_source_fun_name(cls, instance):
        return ".".join(instance.source.imports + instance.source.path)

    @classmethod
    def get_code_fun_def_params(cls, instance) -> list:
        return [p.get_code_fun_def() for p in cls.get_code_params(instance)]

    @classmethod
    def get_code_fun_annotation(cls, instance):
        output = cls.get_code_output(instance)
        if output:
            return output.type.python_type_annotation
        else:
            return "None"

    @classmethod
    def get_code_params(cls, instance):
        params = []
        if instance.input:
            params.append(instance.input)
        for arg in instance.arguments.values():
            params.append(arg)
        for opt in instance.options.values():
            params.append(opt)
        return params

    @classmethod
    def get_code_call_params(cls, instance):
        return cls.get_code_params(instance)

    @classmethod
    def get_code_output(cls, instance):
        return instance.output

    @classmethod
    def get_code_fun_body(cls, instance):
        result = cls.get_code_fun_body_call(instance)
        if instance.output:
            wrap_fun = cls.get_code_wrap_function(instance, instance.output)
            if wrap_fun:
                wrap_args = cls.get_code_wrap_arguments(instance, instance.output) or ""
                if wrap_args:
                    wrap_args = "," + wrap_args
                result = IndentedCodeBlock(
                    "return %s(" % wrap_fun, result, wrap_args, footer=")"
                )
            else:
                result = IndentedCodeBlock("return (", result, footer=")")

        return result

    @classmethod
    def get_code_fun_body_call_params(cls, instance) -> list:
        params = cls.get_code_params(instance)
        call_params = cls.get_code_call_params(instance)

        lines = []
        for p, cp in zip(params, call_params):
            wrap_fun = cls.get_code_wrap_function(instance, cp)
            if wrap_fun:
                wrap_args = cls.get_code_wrap_arguments(instance, cp) or ""
                if wrap_args:
                    wrap_args = ", " + wrap_args
                line = "%s=%s(%s%s)" % (cp.name, wrap_fun, p.name, wrap_args)
            else:
                line = "%s=%s" % (cp.name, p.name)

            lines.append(line)

        return lines

    @classmethod
    def get_code_wrap_function(cls, instance, param):
        return ""

    @classmethod
    def get_code_wrap_arguments(cls, instance, param):
        return ""

    @classmethod
    def get_code_fun_body_call(cls, instance):
        fun_name = cls.get_code_source_fun_name(instance)
        params_code = CommaJoinedCodeBlock(*cls.get_code_fun_body_call_params(instance))
        result = IndentedCodeBlock(fun_name + "(", params_code, footer=")")
        return result
