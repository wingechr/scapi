import os
import sys
import datetime
import json
import importlib
from collections import OrderedDict


def json_serialize(x):
    if isinstance(x, datetime.datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(x, datetime.date):
        return x.strftime("%Y-%m-%d")
    elif isinstance(x, datetime.time):
        return x.strftime("%H:%M:%S")
    else:
        raise NotImplementedError(type(x))


def text_dump(data, filepath):
    data_s = str(data)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(data_s)


def text_load(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def json_dump(data, filepath):
    data_s = json.dumps(
        data, indent=2, sort_keys=True, ensure_ascii=False, default=json_serialize
    )
    text_dump(data_s, filepath)    

def json_load(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def json_cache(filepath, function):
    if not os.path.exists(filepath):
        json_dump(function(), filepath)
    return json_load(filepath)


class Importer:
    paths = set()
    modules = dict()
    objects = dict()

    @classmethod
    def get(cls, module, package=None, paths=None, attributes=None):
        # add new paths
        for path in paths or []:
            path = os.path.abspath(path)
            if path not in cls.paths:
                sys.path.append(path)
                cls.paths.add(path)
        
        # get module
        module_key = (package, module)
        if module_key not in cls.modules:
            cls.modules[module_key] = importlib.import_module(module, package=package)
        result = cls.modules[module_key]
        
        # go down attributes
        for attr in attributes:
            result = getattr(result, attr)
        
        return result




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
    else:
        return process_node(node, path)