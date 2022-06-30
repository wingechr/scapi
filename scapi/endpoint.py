#!/usr/bin/env python3
from collections import OrderedDict

from .build_utils import add_into_tree, iter_tree
from .classes import Argument, Input, Option, Output, Source
from .code import IndentedCodeBlock


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

    @classmethod
    def get_signature_parameters(cls, instance):
        params = []
        if instance.input:
            params.append(instance.input)
        for arg in instance.arguments.values():
            params.append(arg)
        for opt in instance.options.values():
            params.append(opt)
        return params

    @classmethod
    def get_signature_output(cls, instance):
        return instance.output

    # ---------------------------
    # code generation
    # ---------------------------

    @classmethod
    def get_code_instances(cls, path=None):
        return iter_tree(
            cls._tree, cls.get_code_group, cls.get_code_instance, path=path
        )

    @classmethod
    def get_code(cls):
        raise NotImplementedError

    @classmethod
    def get_code_group(cls, elements, path):
        raise NotImplementedError

    @classmethod
    def get_code_instance(cls, instance, path):
        raise NotImplementedError

    @classmethod
    def get_code_fun_name(cls, instance):
        return instance.name_short

    @classmethod
    def get_code_fun_signature(cls, instance):
        name = cls.get_code_fun_name(instance)
        params = cls.get_signature_parameters(instance)
        output = cls.get_signature_output(instance)
        return "def %s(%s) -> %s:" % (
            name,
            ", ".join(p.get_code_fun_def() for p in params),
            output.type.python_type_annotation if output else "None",
        )

    @staticmethod
    def wrap_function(code, output, wrap_fun=None):
        if not output:
            return code
        if not wrap_fun:
            return IndentedCodeBlock("return (", code, footer=")")
        else:
            schema = '"%s"' % output.type.content if output.type.content else "None"
            return IndentedCodeBlock(
                "return %s(" % wrap_fun, code, footer=", %s)" % schema
            )
        return code
