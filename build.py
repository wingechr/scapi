#!/usr/bin/env python3

import logging
import os
import re
import shutil
from collections import OrderedDict

import click
import jsonschema


from utils import json_load, text_dump

class ApiParameter:
    """superclass for arguments/options/input"""

    def __init__(self, name, description=None, default=None, nameOrigin=None):
        self.name = name
        self.description = description or ''
        self.default = default
        self.nameOrigin = nameOrigin or self.name
        
    @property
    def function_def(self):
        result = self.name
        if self.annotation:
            result += ": " + self.annotation
        if self.default:
            result += "=" + str(self.default)
        return result
    
    @property
    def docstring(self):        
        line = self.name        
        if self.annotation:
            line += "(" + self.annotation + ')'
        line += ": " + self.description
        result = IndentedCodeBlock(
            line
        )        
        if self.default is not None:
            result += "default: " + self.default
        return result

    @property
    def annotation(self):
        return None
    

class Argument(ApiParameter):
    """position argument / url part"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def str_pattern(self):
        """return str pattern for url"""
        # TODO: this is only the default
        return "[^/?]+"
        
class Option(ApiParameter):
    """named argument / query"""
    def __init__(self, **kwargs):
        kwargs["default"] = str(kwargs.get("default"))
        super().__init__(**kwargs)
    
    @property
    def annotation(self):
        return "str"

class Data:
    """Superclass for data input/output"""
    pass

class Input(ApiParameter, Data):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Output(Data):
    @property
    def annotation(self):
        return "str"
    
    @property
    def docstring(self):
        return self.annotation + ": TODO output description"

class Callable:
    """Callable in underlying base code"""
    def __init__(self, imports, attributes):
        self.imports = imports
        self.attributes = attributes
        
    @property
    def str_call(self):
        return '.'.join(self.imports + self.attributes)

 
def append_commas(iterable):
    iterable = list(iterable)
    for i in range(len(iterable) - 1):
        iterable[i] += ','
    return iterable

class Endpoint:
    """api endpoint (callable/url/click command"""

    tree_api = {}
    tree_url = {}
    endpoints = []

    @staticmethod
    def get_imports(endpoints):
        imports = set()
        for ep in endpoints:
            imports.add(tuple(ep.callable.imports))
        return [".".join(x) for x in sorted(imports)]
    
    @staticmethod
    def get_all_imports():
        return Endpoint.get_imports(Endpoint.endpoints)
    
    def __init__(self, path, callable, arguments=None, options=None, input=None, output=None, httpMethod=None, description=None):
        
        
        self.callable = Callable(**callable)
        self.arguments = OrderedDict((a["name"], Argument(**a)) for a in arguments or [])
        self.options = OrderedDict((o["name"], Option(**o)) for o in options or [])
        self.input = Input(**input) if input is not None else None
        self.output = Output(**output) if output is not None else None
        self.httpMethod = self.determineHttpMethod(httpMethod, input)
        self.description = description or ""
        self.api_fun_name = path[-1]
        
        self.path_api = path
        self.path_url = self.get_url_path(httpMethod)
        
        self.add_into_tree(self.tree_api, self.path_api)
        self.add_into_tree(self.tree_url, self.path_url)
        self.endpoints.append(self)
    
    def get_url_path(self, httpMethod):
        result = self.path_api.copy()
        # if httpMethod is explicitly stated, the last part of the path will be dropped in the url
        if httpMethod:
            result.pop()
        # add pattern from arguments
        for name, arg in self.arguments.items():
            result.append('^(?<' + name + '>' + arg.str_pattern + ')$')
        
        # add httpMethod (implicitly determined) to path, prefixed by "/"
        result.append("/" + self.httpMethod)        
        return result
    
    def add_into_tree(self, tree, path):
        path, name = path[:-1], path[-1]
        for p in path:
            if p not in tree:
                tree[p] = {}
            tree = tree[p]
        if name in tree:
            raise Exception(path)
        tree[name] = self
    


    @staticmethod
    def determineHttpMethod(httpMethod, input):
        if httpMethod:
            return httpMethod
        elif input:
            return 'POST'
        else:
            return 'GET'
    
    @property
    def url_pattern(self):
        return '(?P<' + self.urlArgument.name + '>[^/?]+)' if self.urlArgument else None
    
    @property
    def str_callable(self):
        return ".".join(self.path_callable)

    @property
    def path_callable(self):
        return self.callable.imports + self.callable.attributes    

    @property
    def str_api(self):
        return "api." + ".".join(self.path_api)
    
    @property
    def str_url(self):
        return "/" + "/".join(self.path_url)
    
    @property
    def pattern_url(self):
        pat = "^%s %s" % (self.httpMethod, self.str_url)
        if self.url_pattern:
            pat += '/' + self.url_pattern
        pat += '$'
        return pat

    
    @property
    def api_parameters(self):
        params = []
        params += list(self.arguments.values())
        if self.input:
            params += [self.input]
        params += list(self.options.values())
        return params

    
        
    @property
    def docstring(self):
        result = CodeBlock(
            '"""' + self.description,
            None            
        )        
        if self.api_parameters:            
            result += IndentedCodeBlock(
                "Args:",
                [p.docstring for p in self.api_parameters]
            )
        
        if self.output:
             result += IndentedCodeBlock(
                "Returns:",
                self.output.docstring
            )

        result += ['"""']
        return result
    
    @property
    def api_function(self):
        fun_annotation = self.output.annotation if self.output else "None"
        fun_args = ", ".join(a.function_def for a in self.api_parameters)

        result = IndentedCodeBlock(
            CodeBlock(
                "@staticmethod",
                "def " + self.api_fun_name + "(" + fun_args + ") -> " + fun_annotation + ":"
            ),
            self.docstring
        )
        
        call_args = append_commas("%s=utils.validate(%s, %s)" % (p.nameOrigin, p.name, p.annotation) for p in self.api_parameters)
        

        if self.output:
            call = IndentedCodeBlock(self.callable.str_call + "(", *call_args, footer='),')
            result += IndentedCodeBlock('return utils.validate(', call, self.output.annotation, footer=')')            
        else:
            call = IndentedCodeBlock(self.callable.str_call + "(", *call_args, footer=')')
            result += call


        return result

    @classmethod
    def get_api_code(cls, node=None, class_name=None):
        node = node or cls.tree_api
        if isinstance(node, dict):
            items = [cls.get_api_code(child, name) for name, child in node.items()]
            if class_name:
                return IndentedCodeBlock(
                    "class " + class_name + ':',
                    *items
                )
            else:
                return CodeBlock(*items)
        else:
            return CodeBlock(node.api_function)
    
    @classmethod
    def get_server_router(cls, node=None, class_name=None):
        node = node or cls.tree_url
        if isinstance(node, dict):
            items = [cls.get_server_router(child, name) for name, child in node.items()]
            if class_name:
                return IndentedCodeBlock(
                    '"' + class_name + '": {',
                    *append_commas(items),
                    footer="}"
                )
            else:
                return CodeBlock(*items)
        else:
            return CodeBlock(node)

class CodeBlock():
    """lines of code in same indentation"""
    def __init__(self, *parts):
        self.parts = []
        if parts:
            self += parts
    
    def __add__(self, it):
        if it is None:
            self.parts.append(None)
        elif isinstance(it, (list, tuple)):
            for i in it:
                self += i
        elif isinstance(it, CodeBlock):
            self.parts.append(it)
        else:
            for line in str(it).splitlines(keepends=False):
                self.parts.append(line.strip())
        return self

    def get_indented_lines(self, level):
        for p in self.parts:
            if not p:
                yield ""
            elif isinstance(p, str):
                yield self.indent(level) + p
            else: # Codeblock
                yield from p.get_indented_lines(level)
    
    def __str__(self):
        return '\n'.join(self.get_indented_lines(0))
    
    @staticmethod
    def indent(level):
        return " " * 4 * level

class IndentedCodeBlock(CodeBlock):
    def __init__(self, header, *parts, footer=None):
        self.header = CodeBlock(header)
        self.footer = CodeBlock(footer)
        super().__init__(*parts)
    
    def get_indented_lines(self, level):
        yield from self.header.get_indented_lines(level)
        yield from super().get_indented_lines(level + 1)
        yield from self.footer.get_indented_lines(level)

class Script(CodeBlock):
    name = None    

    def __init__(self, *parts):
        super().__init__(
            'from . import utils',
            'import logging',
            *parts
        )

    def save(self, output_path):
        text_dump(str(self), output_path + '/' + self.name + '.py')


class Script_1_Api(Script):
    name = "api"

    def __init__(self):        
        super().__init__(                        
            "import sys",
            None,
            IndentedCodeBlock(
                "def Api(python_paths=None):",                
                "sys.path += (python_paths or [])",                
                *["import " + i for i in Endpoint.get_all_imports()],
                None,
                None,
                IndentedCodeBlock(
                    "class Api:",
                    Endpoint.get_api_code()
                ),
                "return Api"                               
            )
        )        

class Script_2_Server(Script):
    name = "server"

    def __init__(self):
        super().__init__(
            "import os",
            None,        
            IndentedCodeBlock(
                "def router():",
                IndentedCodeBlock(
                    "return {",
                    Endpoint.get_server_router(),
                    footer="}"
                ),
            ),
            'application = utils.create_wsgi_application(router)',
            None,
            IndentedCodeBlock(
                'if __name__ == "__main__":',
                'port = int(os.environ.get("SERVER_PORT", "8000"))',
                'utils.start_wsgi_server(application, port=port)'                
            )
        )

class Script_3_Client(Script):
    name = "cli"

    def __init__(self):
        super().__init__()

class Script_4_Cli(Script):
    name = "cli"

    def __init__(self):
        super().__init__()
    



@click.command()
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def main(schema_json, output_path):
    
    SRC_DIR = os.path.abspath(os.path.dirname(__file__))

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load(SRC_DIR + "/schema/api.json")
    jsonschema.validate(schema, metaschema)

    # create output directory
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # copy schema + files from shared
    for name in os.listdir(SRC_DIR + '/shared'):
        if not name.endswith('.py'):
            continue
        shutil.copy(SRC_DIR + '/shared/' + name, output_path + '/' + name)
    shutil.copy(schema_json, output_path + '/schema.json')
    
    # create endpoints
    _endpoints = [Endpoint(**ep) for ep in schema["endpoints"]]
    
    # generate code for layers
    Script_1_Api().save(output_path)
    Script_2_Server().save(output_path)
    Script_3_Client().save(output_path)
    Script_4_Cli().save(output_path)

    
if __name__ == "__main__":
    main(prog_name="python3 build.py")
