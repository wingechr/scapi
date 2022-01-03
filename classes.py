#!/usr/bin/env python3
from copy import deepcopy

type_to_python_type = {
    "boolean": "bool",
    "string": "str",
    "integer": "int",
    "number": "float",
    "bytes": "bytes",
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

        self.content_params = dict()
        for idx, part in enumerate((self.content or "").split(";")):
            if idx == 0:
                key, name = "type", part
            else:
                key, name = part.split("=")
            self.content_params[key.strip().lower()] = name.strip()

    def __str__(self):
        return self.click_repr

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
    def python_type_validation(self):
        if self.multiple:
            return "list"
        if self.content:
            return "object"
        if self.type:
            return type_to_python_type[self.type]
        return "None"

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


class Parameter:
    """superclass for arguments/options/input"""

    def __init__(self, name=None, type=None, description=None, source=None):
        self.name = name
        self.type = Type(**(type or {}))
        self.description = description
        self.source = source or self.name
        if not self.description:
            raise Exception("Missing description for %s" % self.name)

    # def get_modified(self, type=None):
    #    copy = deepcopy(self)
    #    if type:
    #        copy.type = Type(**type)
    #    copy.source = copy.name
    #    return copy

    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name
        result += ": " + self.type.python_type_annotation
        result += "=None"
        return result

    def get_code_docstring(self):
        if not self.name:
            raise Exception("no name")
        result = self.name
        result += "(" + self.type.python_type_annotation + ")"
        result += ":"  # always add the colon!
        result += " " + self.description
        return result

    @property
    def click_help(self):
        return self.description.replace("\n", " ")


class Argument(Parameter):
    """position argument / url part"""

    def __init__(self, name, type, description=None, source=None, **_kwargs):
        super().__init__(name=name, type=type, description=description, source=source)

    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name
        result += ": " + self.type.python_type_annotation
        return result


class Option(Parameter):
    """named argument / query"""

    def __init__(self, name, type, description=None, source=None, **_kwargs):
        super().__init__(name=name, type=type, description=description, source=source)

    def get_code_docstring(self):
        result = super().get_code_docstring()
        return result


class Input(Argument):
    pass


class Output(Parameter):
    def __init__(self, type, description=None, **_kwargs):
        super().__init__(type=type, description=description)

    def get_code_docstring(self):
        result = self.type.python_type_annotation
        if self.description:
            result += ": " + self.description
        return result


class Source:
    """source in underlying base code"""

    def __init__(self, imports, path):
        self.imports = imports or []
        self.path = path or []
