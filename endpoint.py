#!/usr/bin/env python3

from collections import OrderedDict

from code import CodeBlock, IndentedCodeBlock, CommaJoinedCodeBlock
from shared.types import Type

def add_into_tree(tree, element, path):
    # add self into tree
    path, name = path[:-1], path[-1]
    for p in path:
        if p not in tree:
            tree[p] = OrderedDict()
        tree = tree[p]
    if name in tree:
        raise Exception(path)
    tree[name] = element
    

def iter_tree(node, process_group, process_node, path=None):
    path = path or []
    if isinstance(node, OrderedDict):
        # its a group:
        items = []
        for name, node in node.items():
            items.append(iter_tree(node, process_group, process_node, path=path + [name]))
        return process_group(items, path)
    elif isinstance(node, Endpoint):
        return process_node(node, path)
    else:
        raise Exception(type(node))


class Endpoint:

    _tree = OrderedDict()
    _instances = []
    
    def __init__(self, path, source, arguments=None, options=None, input=None, output=None, http=None, description=None):        
        self.description = description
        self.path = path
        self._http = http
        self.source = Source(**source)
        self.arguments = OrderedDict((a["name"], Argument(**a)) for a in arguments or [])
        self.options = OrderedDict((o["name"], Option(**o)) for o in options or [])
        self.input = Input(**input) if input is not None else None
        self.output = Output(**output) if output is not None else None  
        
        add_into_tree(self._tree, self, self.path)
        self._instances.append(self)

    @property
    def name_short(self):
        return self.path[-1]
    
    @property
    def name_long(self):
        return '_'.join(self.path)

    @property
    def http(self):
        if self._http:
            return self._http
        elif self.input:
            return 'POST'
        else:
            return 'GET'
    
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
    def get_code_group(cls, elements, path):
        return CodeBlock(*elements)
        
    @classmethod
    def get_code_instances(cls, path=None):
        return iter_tree(cls._tree, cls.get_code_group, cls.get_code_instance, path=path)        

    @classmethod
    def get_code(cls):
        return cls.get_code_instances()
    
    @classmethod
    def get_code_fun_decorators(cls, instance):
        return []

    @classmethod
    def get_code_instance(cls, instance, path):
        return CodeBlock(
            None,
            IndentedCodeBlock(
                CodeBlock(
                    *cls.get_code_fun_decorators(instance),
                    cls.get_code_fun_signature(instance),
                ),
                cls.get_code_fun_docstring(instance),
                cls.get_code_fun_body(instance)
            )
        )

    @classmethod
    def get_code_fun_name(cls, instance):
        return instance.name_short
    
    @classmethod
    def get_code_source_fun_name(cls, instance):
        return '.'.join(instance.source.imports + instance.source.path)
    
    @classmethod
    def get_code_fun_def_params(cls, instance):    
        return [
            p.get_code_fun_def() for p in cls.get_code_params(instance)
        ]
    
    @classmethod
    def get_code_fun_annotation(cls, instance):    
        output = cls.output_mod(instance)
        if output:
            return output.type.python_type_annotation
        else:
            return "None"

    @classmethod
    def get_code_fun_signature(cls, instance):    
        return "def %s(%s) -> %s:" % (
            cls.get_code_fun_name(instance),
            ', '.join(cls.get_code_fun_def_params(instance)),
            cls.get_code_fun_annotation(instance),
        )

    @classmethod
    def get_code_fun_docstring(cls, instance):
        result = CodeBlock('"""%s' % instance.description)
        params = cls.get_code_params(instance)
        output = cls.output_mod(instance)
        if params:
            result += None
            result += IndentedCodeBlock(
                "Args:",
                *[p.get_code_docstring() for p in params]
            )
        if output:
            result += None
            result += IndentedCodeBlock(
                "Returns:",
                output.get_code_docstring()
            )

        result += '"""'
        return result
    
    @classmethod
    def wrap_params_name(cls):
        return None
    
    @classmethod
    def wrap_return_name(cls):
        return None
    
    @classmethod
    def wrap_params(cls, param):
        if cls.wrap_params_name():
            return '%s.%s(%s)' % (param.type.python_repr, cls.wrap_params_name(), param.name)
        else:
            return param.name

    @classmethod
    def output_mod(cls, instance):
        return instance.output

    @classmethod
    def get_code_fun_body(cls, instance):
        params = cls.get_code_params(instance)
        fun_name = cls.get_code_source_fun_name(instance)
        params_code = CommaJoinedCodeBlock(*["%s=%s" % (p.source, cls.wrap_params(p)) for p in params])
        output = cls.output_mod(instance)

        if output:
            if cls.wrap_return_name():
                wrap_return = '%s.%s' % (output.type.python_repr, cls.wrap_return_name())
                result = IndentedCodeBlock(
                    "return " + wrap_return + "(",
                    IndentedCodeBlock(
                        fun_name + "(",
                        params_code,
                        footer=")"
                    ),
                    footer=")"
                )
            else:
                result = IndentedCodeBlock(
                    "return " + fun_name + "(",
                    params_code,
                    footer=")"
                )
        else:
            result = IndentedCodeBlock(
                fun_name + "(",
                params_code,
                footer=")"
            )

            
                

        return result
        

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


class EndpointApi(Endpoint):
    @classmethod
    def get_code(cls):
        code_imports = CodeBlock(*["import " + i for i in cls.get_imports()])
        code_main = CodeBlock(
            code_imports,            
            cls.get_code_instances(path=['api'])
        )
        code_wrapped = IndentedCodeBlock(
            "def api():",
            None,
            code_main,
            None,
            "return api"

            
        )

        return code_wrapped
    
    @classmethod
    def get_code_group(cls, elements, path):
        name = path[-1]
        return CodeBlock(None, IndentedCodeBlock("class %s:" % name, *elements))

    
    @classmethod
    def get_imports(cls):
        imports = set()
        for ep in cls._instances:
            imports.add(tuple(ep.source.imports))
        return [".".join(x) for x in sorted(imports)]
   
    @classmethod
    def wrap_params_name(cls):
        return "validate"
    
    @classmethod
    def wrap_return_name(cls):
        return "validate"

    @classmethod
    def get_code_fun_decorators(cls, instance): 
        return [
            "@staticmethod"
        ]


    
class EndpointServer(Endpoint):
    @classmethod
    def get_code_fun_name(cls, instance):    
        return 'route_' + instance.name_long
    
    @classmethod
    def get_code_source_fun_name(cls, instance):
        return '.'.join(["api"] + instance.path)

    @classmethod
    def output_mod(cls, instance):
        if instance.output:
            return Output(
                "bytes", description=instance.output.description
            )
        else:
            return None
    
    @classmethod
    def get_code_params(cls, instance):    
        params = []
        if instance.input:
            params.append(
                Input(
                    name=instance.input.name,
                    type="bytes",
                    description=instance.input.description
                )
            )
        for arg in instance.arguments.values():
            params.append(
                Argument(
                    name=arg.name,
                    type="array",
                    description=arg.description
                )
            )
        for opt in instance.options.values():
            params.append(
                Option(
                    name=opt.name,
                    type="array",
                    description=opt.description                    
                )
            )
        return params
    
    @classmethod
    def get_code_fun_decorators(cls, instance):
        path_url_str = ['"%s"' % p for p in instance.path_url]
        path_args = ['"%s"' % a.name for a in instance.arguments.values()]        
        input_str = '"%s"' % instance.input.name if instance.input else "None"
        return [
            '@route("%s", [%s], [%s], %s)' % (instance.http, ", ".join(path_url_str), ", ".join(path_args), input_str)
        ]

class EndpointClient(EndpointApi):
    @classmethod
    def get_code_fun_body(cls, instance):
        params = cls.get_code_params(instance)
        output = cls.output_mod(instance)

        base_url = '/'.join(instance.path_url + ["%s" for _ in instance.arguments])
        substs = ", ".join(instance.arguments)
        if substs:
            url = '"%s" %% (%s)' % (base_url, substs)
        else:
            url = '"%s"' % (base_url,)
        kwargs = "{%s}" % ", ".join('"%s": %s' % (o.name, o.name) for o in instance.options.values())
        if instance.input:
            data = "encode(%s)" % instance.input.name
        else:
            data = "None"



        result = IndentedCodeBlock(
            'request(',
            CommaJoinedCodeBlock(
                '"%s"' % instance.http, 
                url, 
                "params=%s" % kwargs, 
                "data=%s" % data
            ),
            footer=')'                         
        )

        #if output:
        #    result = Inde
        # ntedCodeBlock(
        #        "return "
        #    )
        
        return result
    
    @classmethod
    def get_code(cls):
        return CodeBlock(
            cls.get_code_instances(path=['api'])
        )

class EndpointCli(EndpointServer):
    @classmethod
    def get_code_fun_name(cls, instance):    
        return 'main_' + instance.name_long
    
    @classmethod
    def get_code_group(cls, elements, path):
        if path:
            path = ["main"] + path
            group_path, name = path[:-1], path[-1]
            supergroup_name = '_'.join(group_path)
            group_name = '_'.join(path)

            return CodeBlock(
                CodeBlock(
                    None,
                    '@%s.group("%s")' % (supergroup_name, name),
                    IndentedCodeBlock(
                        "def %s():" % group_name,
                        "pass"
                    ),
                    None,
                ),
                CodeBlock(*elements)
            )
        else:
            return CodeBlock(*elements)

    @classmethod
    def output_mod(cls, instance):
        return None
    
    @classmethod
    def get_code_params(cls, instance):    
        params = []
        # no input        
        for arg in instance.arguments.values():
            params.append(arg)
        for opt in instance.options.values():
            params.append(opt)
        return params
    
    @classmethod
    def get_code_fun_decorators(cls, instance):
        path = ["main"] + instance.path
        group_path, name = path[:-1], path[-1]
        group_name = '_'.join(group_path)

        result = []
        result.append('@%s.command("%s")' % (group_name, name))

        for a in instance.arguments.values():
            result.append('@click.argument("%s", click.%s)' % (a.name, a.type.click_repr))
        for o in instance.options.values():
            result.append('@click.option("--%s", click.%s, help="%s")' % (o.name, o.type.click_repr, o.description))
        
        return result
    

class Parameter:
    """superclass for arguments/options/input"""
    def __init__(self, name=None, type=None, description=None, default=None, source=None):
        self.name = name
        self.type = Type(type=type) if type else Type(type="null")
        self.description = description
        self.default = default
        self.source = source or self.name
    
    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name        
        result += ': ' + self.type.python_type_annotation
        result += '=' + str(self.default)
        return result

    def get_code_docstring(self):
        if not self.name:
            raise Exception("no name")
        result = self.name        
        result += '(' + self.type.python_type_annotation + ')'
        result += ":" # always add the colon!
        result += ' ' + (self.description or 'TODO: description')
        return result

class Argument(Parameter):
    """position argument / url part"""
    def __init__(self, name, type, description=None, source=None, **_kwargs):
        super().__init__(
            name=name, 
            type=type, 
            description=description, 
            source=source
        )
    
    def get_code_fun_def(self):
        if not self.name:
            raise Exception("no name")
        result = self.name        
        result += ': ' + self.type.python_type_annotation
        return result
        
class Option(Parameter):
    """named argument / query"""
    def __init__(self, name, type, description=None, source=None, default=None, **_kwargs):
        super().__init__(
            name=name, 
            type=type, 
            description=description, 
            source=source,
            default=default
        )

    def get_code_docstring(self):
        result = super().get_code_docstring()
        if self.default:
            result += ' Defaults to %s' % self.default
        return result


class Input(Argument):
    pass


class Output(Parameter):
    def __init__(self, type, description=None, **_kwargs):
        super().__init__(
            type=type, 
            description=description
        )
    
    def get_code_docstring(self):
        result = self.type.python_type_annotation
        if self.description:
            result += ': ' + self.description
        return result

class Source:
    """source in underlying base code"""
    def __init__(self, imports, path):
        self.imports = imports or []
        self.path = path or []
    
    