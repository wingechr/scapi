#!/usr/bin/env python3
from collections import OrderedDict
from copy import deepcopy

from .build_utils import underscore_props

type_to_python_type = {
    "boolean": "bool",
    "string": "str",
    "integer": "int",
    "number": "float",
    "bytes": "bytes",
    "object": "object",
}
type_to_click_type = {
    "boolean": "BOOL",
    "string": "STRING",
    "integer": "INT",
    "number": "FLOAT",
}


class Type:
    def __init__(self, type=None, multiple=False, content=None):
        if bool(content) == bool(type):
            raise Exception("Must be EITHER type OR content")
        if content and multiple:
            raise Exception("content cannot have multiple")

        self.type = type
        self.multiple = multiple
        self.content = content

        self._content_params = dict()
        for idx, part in enumerate((self.content or "").split(";")):
            if idx == 0:
                key, name = "type", part
            else:
                key, name = part.split("=")
            self._content_params[key.strip().lower()] = name.strip()

    def __str__(self):
        return self.click_repr

    @property
    def content_params(self):
        return self._content_params

    @property
    def python_type_annotation(self):
        if self.multiple:
            return "list"
        if self.content:
            return "object"
        if self.type:
            return type_to_python_type[self.type]
        return "None"

    @property
    def python_type_annotation_single(self):
        if self.type:
            return type_to_python_type[self.type]
        if self.content:
            return "object"
        return "None"

    @property
    def python_type_validation(self):
        d = {}
        if self.multiple:
            d["type"] = "array"
            d["items"] = {"type": self.type}
        else:
            d["type"] = self.type

        return repr(d)

    @property
    def click_repr(self):
        if self.type == "boolean":
            if self.multiple:
                raise Exception("bool cannot be multiple")
            result = "is_flag=True"
        elif self.type:
            t = type_to_click_type[self.type]
            result = "type=utils.click.types.%s" % t
            if self.multiple:
                result += ", multiple=True"
        else:
            raise Exception("cannot create click paramater for data")
        return result


class Parameters:
    """"""

    def __init__(self, arguments, output_data, input_data=None, resource_id=None):
        self.arguments = OrderedDict()
        for a in arguments:
            a = Argument(**underscore_props(a))
            assert a.name not in self.arguments
            self.arguments[a.name] = a

        self.output_data = OutputData(**underscore_props(output_data))
        self.input_data = (
            InputData(**underscore_props(input_data)) if input_data else None
        )
        self.resource_id = (
            ResourceId(**underscore_props(resource_id)) if resource_id else None
        )


class Parameter:
    def __init__(self, name, type, description, name_target=None):
        self.name = name
        self.type = type
        self.name_target = name_target or self.name
        self.description = description

    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name
        result += ": " + self.type.python_type_annotation
        if self.has_default:
            result += "=%s" % self.default
        return result

    def get_code_docstring(self):
        if not self.name:
            raise Exception("no name")
        result = self.name

        result += "(" + self.type.python_type_annotation + ")"

        result += ":"  # always add the colon!

        if self.type.multiple:
            # also show types of elements
            result += " List of %s." % self.type.python_type_annotation_single
        elif self.type.content_params.get("schema"):
            # also show content type
            result += " Data schema is %s." % self.type.content_params.get("schema")

        result += " " + self.description
        return result

    @property
    def click_help(self):
        return self.description.replace("\n", " ")

    def as_bytes(self):
        copy = deepcopy(self)
        copy.type = Type(type="bytes")
        return copy

    def as_string(self):
        copy = deepcopy(self)
        copy.type = Type(type="string")
        return copy

    @property
    def has_default(self):
        return True

    @property
    def default(self):
        return None


class Argument(Parameter):
    """position argument / url part"""

    def __init__(self, name, type, description, name_target=None):
        super().__init__(name, Type(**type), description)
        self.name_target = name_target or self.name

    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name
        result += ": " + self.type.python_type_annotation
        return result


class InputData(Parameter):
    def __init__(self, name, content, description, name_target="data"):
        super().__init__(name, Type(content=content), description)

    def get_code_docstring(self):
        result = self.type.python_type_annotation + ":"

        if self.type.content_params.get("schema"):
            # also show content type
            result += " Data schema is %s." % self.type.content_params.get("schema")

        if self.description:
            result += " " + self.description
        return result

    @property
    def has_default(self):
        return False


class ResourceId(Parameter):
    def __init__(self, name, type, description, name_target="id"):
        super().__init__(name, Type(**type), description)


class OutputData(Parameter):
    def __init__(self, content, description):
        super().__init__(None, Type(content=content), description)

    def get_code_docstring(self):
        result = self.type.python_type_annotation + ":"

        if self.type.content_params.get("schema"):
            # also show content type
            result += " Data schema is %s." % self.type.content_params.get("schema")

        if self.description:
            result += " " + self.description
        return result


class Source:
    """source in underlying base code"""

    def __init__(self, imports, path):
        self.imports = imports
        self.path = path


class Target:
    """TODO"""

    def __init__(self, path, verb=None):
        self.verb = verb
        self.path = path
