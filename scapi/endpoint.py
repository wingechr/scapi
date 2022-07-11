#!/usr/bin/env python3
from collections import OrderedDict

from .build_utils import add_into_tree, iter_tree, underscore_props
from .classes import Parameters, Source, Target
from .code import IndentedCodeBlock


class Endpoint:

    _tree = OrderedDict()
    _instances = []

    def __init__(
        self,
        target,
        source,
        parameters,
        description,
        examples=None,
        authorization=None,
    ):
        self.target = Target(**underscore_props(target))
        self.source = Source(**underscore_props(source))
        self.parameters = Parameters(**underscore_props(parameters))
        self.description = description
        self.authorization = authorization

        add_into_tree(self._tree, self, self.path)
        self._instances.append(self)

    @property
    def path(self):
        return self.target.path

    @property
    def name_short(self):
        return self.path[-1]

    @property
    def name_long(self):
        return "_".join(self.path)

    @property
    def http(self):
        if self.target.verb:
            return self.target.verb
        elif self.parameters.input_data:
            return "POST"
        else:
            return "GET"

    @property
    def path_url(self):
        if self.target.verb:
            path = self.path[:-1]
        else:
            path = self.path[:]
        return path

    @classmethod
    def get_signature_parameters(cls, instance):
        params = []
        if instance.parameters.input_data:
            params.append(instance.parameters.input_data)
        for arg in instance.parameters.arguments.values():
            params.append(arg)
        return params

    @classmethod
    def get_signature_output(cls, instance):
        return instance.parameters.output_data

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
