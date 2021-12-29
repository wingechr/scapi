#!/usr/bin/env python3

import logging
import os

import click
import coloredlogs
import jsonschema

from collections import OrderedDict

from utils import json_load, text_load, text_dump


# https://coloredlogs.readthedocs.io/en/latest/api.html#changing-the-date-time-format
coloredlogs.DEFAULT_LOG_FORMAT = "[%(asctime)s %(levelname)7s] %(message)s"
coloredlogs.DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
coloredlogs.DEFAULT_FIELD_STYLES = {
    "asctime": {"color": "black", "bold": True},  # gray
    "levelname": {"color": "black", "bold": True},  # gray
}
coloredlogs.DEFAULT_LEVEL_STYLES = {
    "debug": {"color": "black", "bold": True},  # gray
    "info": {"color": "white"},
    "warning": {"color": "yellow"},
    "error": {"color": "red", "bold": 10},
}


def load_template(name, context=None):
    template_path = os.path.dirname(__file__) + '/templates'
    file_path = template_path + '/' + name + '.py'
    data = text_load(file_path)
    for k, v in (context or {}).items():
        data = data.replace("'''{{" + k + "}}'''", v)
    return data

def save_script(data, output_path, name):
    file_path = output_path + '/' + name + '.py'
    text_dump(data, file_path)


class Argument:
    def __init__(self, name, description=None):
        self.name = name
        self.isInputData = False
        self.isUrl = False
        self.description = description

class Callable:
    _imports = set()

    def __init__(self, imports, attributes):
        self.imports = imports
        self.attributes = attributes
        self._imports.add(".".join(self.imports))

    @classmethod
    def get_imports(cls):
        return sorted(cls._imports)


def add_into_tree(tree, path, element):
    path, name = path[:-1], path[-1]
    for p in path:
        if p not in tree:
            tree[p] = {}
        tree = tree[p]
        if not isinstance(tree, dict):
            raise Exception(path)
    assert name not in tree
    tree[name] = element    

class Endpoint:
    
    tree_api = {}
    
    def __init__(self, path, callable, arguments, httpMethod=None, inputDataArgument=None, urlArgument=None, output=None):
        self.callable = Callable(**callable)
        self.arguments = OrderedDict((a["name"], Argument(**a)) for a in arguments)
        self.inputDataArgument = self.arguments[inputDataArgument] if inputDataArgument else None
        self.urlArgument = self.arguments[urlArgument] if urlArgument else None
        if inputDataArgument:        
            self.arguments[inputDataArgument].isInputData = True
        if urlArgument:        
            self.arguments[urlArgument].isUrl = True
        self.httpMethod = self.determineHttpMethod(httpMethod, inputDataArgument)        
        self.path_url = path[:-1] if httpMethod else path
        self.path_api = path
        self.output = output

        add_into_tree(self.tree_api, self.path_api, self)        

    
    @staticmethod
    def determineHttpMethod(httpMethod, inputDataArgument):
        if httpMethod:
            return httpMethod
        elif inputDataArgument:
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


@click.command()
@click.pass_context
# @click.version_option(__version__)
@click.option(
    "--loglevel",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
)
@click.argument("schema_json", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False))
def main(ctx, loglevel, schema_json, output_path):
    """Script entry point."""
    if isinstance(loglevel, str):  # e.g. 'debug'/'DEBUG' -> logging.DEBUG
        loglevel = getattr(logging, loglevel.upper())
    coloredlogs.install(level=loglevel)
    ctx.ensure_object(dict)

    # load and validate schema
    schema = json_load(schema_json)
    metaschema = json_load("G:/scapi/schema/api.json")
    jsonschema.validate(schema, metaschema)
    

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # create endpoints
    endpoints = [Endpoint(**ep) for ep in schema["endpoints"]]
    
    def recursive_lines(dct, indent=1, level=0, get_items=None, format_key=None, format_val=None, header="{", footer="}"):
        if not level:
            yield (0, header)
        
        format_key = format_key or (lambda x: '"%s": ' % str(x))
        format_val = format_val or (lambda x: x)
        get_items = get_items or (lambda x: x.items())
        
        items = sorted(list(get_items(dct)), key=lambda it: it[0])
        for idx, (key, val) in enumerate(items):
            comma = "" if idx + 1 == len(items) else ","
            if isinstance(val, dict):
                yield (indent + 1, '%s%s' % (format_key(key), header))
                yield from recursive_lines(
                    val, 
                    indent=indent + 1,
                    level=level+1,
                    get_items=get_items,
                    format_key=format_key,
                    format_val=format_val,
                    header=header,
                    footer=footer
                )
                yield (indent + 1, "%s%s" % (footer, comma))        
            else:
                yield (indent + 1, '%s%s%s' % (format_key(key), format_val(val), comma))

        if not level:
            yield (indent, footer)
            
    def create_api_namespaces(tree):
        yield from recursive_lines(
            tree, 
            header="SimpleNamespace(", footer=")", 
            format_key=lambda x: "%s=" % x, 
            format_val=lambda x: "validate(%s)" % x.str_callable,
            indent=1
        )

    def client_namespaces_namespaces(tree):
        yield from recursive_lines(
            tree, 
            header="SimpleNamespace(", footer=")", 
            format_key=lambda x: "%s=" % x, 
            format_val=lambda x: 'request("%s", "%s")' % (x.httpMethod, x.str_url),
            indent=1
        )
    

    def create_url(endpoints):
        result = {}
        for ep in endpoints:
            assert ep.pattern_url not in result
            result[ep.pattern_url] = "serve(%s)" % ep.str_api
                
        yield from recursive_lines(result, indent=1)
        
            


    def join_line_indent(lines):
        return '\n'.join(" " * (i*4) + l for i, l in lines)

    context = {}

    context["imports"] = '\n    '.join("import " + imp for imp in Callable.get_imports())
    context["api_namespaces"] = join_line_indent(create_api_namespaces(Endpoint.tree_api))
    script_api = load_template("api", context)    
    save_script(script_api, output_path, "api")

    context["handlers"] = join_line_indent(create_url(endpoints))
    script_server = load_template("server", context)
    save_script(script_server, output_path, "server")

    context["client_namespaces"] = join_line_indent(client_namespaces_namespaces(Endpoint.tree_api))
    script_client = load_template("client", context)
    save_script(script_client, output_path, "client")
   

    def rec_tree(node, level=0, group_name="main"):
        for k, v in node.items():                
            func_name = group_name + '_' + k            
            if isinstance(v, dict):                
                # create group
                
                yield(0, '@%s.group("%s")' % (group_name, k))
                yield(0, "@click.pass_context")
                yield(0, "def %s(ctx):" % func_name)
                yield(1, 'ctx.obj["api"] = getattr(ctx.obj["api"], "%s")' % k)
                yield(0, "")
                yield(0, "")

                yield from rec_tree(v, level=level+1, group_name=func_name)
            else:
                # create function

                yield(0, '@%s.command("%s")' % (group_name, k))
                yield(0, "@click.pass_context")

                args = []
                if v.urlArgument:
                    arg = v.urlArgument
                    yield(0, '@click.argument("%s")' % (arg.name))                                                            
                    args.append(arg.name)
                
                for arg in v.arguments.values():
                    if not (arg.isUrl or arg.isInputData):
                        yield(0, '@click.option("--%s", help="%s")' % (arg.name, arg.description))                                        
                        args.append(arg.name)                

                yield(0, "def %s(%s):" % (func_name, ",".join(["ctx"] + args)))
                yield(1, 'ctx.obj["api"] = getattr(ctx.obj["api"], "%s")' % k)
                
                if v.inputDataArgument:
                    args.insert(0, v.inputDataArgument.name)
                    yield(1, '%s = ctx.obj["stdin"].read()' % (v.inputDataArgument.name))
                if v.output:
                    yield(1, 'result = ctx.obj["api"](%s)' % ", ".join("%s=%s" % (x, x) for x in args))
                    yield(1, 'ctx.obj["stdout"].write(str(result).encode())')
                else:
                    yield(1, 'ctx.obj["api"](%s)' % ", ".join("%s=%s" % (x, x) for x in args))
                yield(0, "")
                yield(0, "")
    
    context["click_functions"] = join_line_indent(rec_tree(Endpoint.tree_api))
    script_cli = load_template("cli", context)
    save_script(script_cli, output_path, "cli")

    # todo env
    save_script("""
import sys
sys.path.append('G:/scapi/mockup/0_code')
    """, output_path, "__init__")


if __name__ == "__main__":
    main(prog_name="python3 build.py")
