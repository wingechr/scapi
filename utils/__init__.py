import os
import sys
import datetime
import json
import importlib


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
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(data)


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


def get_byte_iterator(chunk_size=16777216):
    class ByteIterator:
        
        def __init__(self, data_stream, content_size=None):
            self.data_stream = data_stream
            self.read_bytes = None
            self.chunk_size = chunk_size            
            self.content_size = content_size

        def __enter__(self):
            self.data_stream.__enter__()
            self.read_bytes = 0
            return self

        def __exit__(self, *args):
            self.data_stream.__exit__(*args)            

        def __iter__(self):
            return self

        def __next__(self):
            if self.content_size:
                chunk_size = min(self.content_size - self.read_bytes, self.chunk_size)
            else:
                chunk_size = self.chunk_size
            chunk = self.read(chunk_size)
            if not chunk:
                raise StopIteration()
            self.read_bytes += len(chunk)
            return chunk
        
    return ByteIterator