import urllib.parse  # noqa
from importlib import import_module
from types import SimpleNamespace
from urllib.parse import quote_plus  # noqa

from functools import partial
import click  # noqa


class Obj:
    def __init__(self, data):
        self.data = data
        self.id = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

        
class ObjTab:
    cls = Obj

    def __init__(self):
        self.instances = {}

    def list(self):
        return self.instances.values()

    def __iter__(self):
        return iter(self.list())
    
    def get(self, id):
        return self.instances[id]

    def __getitem__(self, id):
        return self.get(id)

    def delete(self, id):
        del self.instances[id]
    
    def __delitem__(self, id):
        del self.instances[id]

    def create(self, data):
        inst = self.cls(data)
        id = (max(self.instances.keys()) if self.instances else 0) + 1
        inst.id = id
        assert id not in self.instances
        self.instances[id] = inst
        return inst

    def __call__(self, data):
        return self.create(data)


    def replace(self, id, data):
        inst = self.cls(data)
        inst.id = id
        self.instances[id] = inst
    
    def __setitem__(self, id, data):
        return self.replace(id, data)

    
    # update / PATCH unclear
    #def update(self, id, data):
    #    inst = self.instances[id]
    #    inst.data = inst.data + data  # TODO
    #    return inst

    def __str__(self):
        return f"{self.__class__.__name__}()"


class B(Obj):
    pass


class BTab(ObjTab):
    cls = B


class A(Obj):
    def __init__(self, data):
        self.data = data
        self.b = BTab()


class ATab(ObjTab):
    cls = A


def load_db():
    print("load_db")
    main = ATab()
    a1 = main.create("a1")
    a2 = main.create("a2")
    a1.b.create("a1b1")
    a1.b.create("a1b2")
    a2.b.create("a2b1")
    return main


def mk_c(name, attributes, properties, methods, help):
    """
    slots: dict of name -> function (either magic methodor property)
    """

    slots = list(attributes) + list(properties) + list(methods)

    class C:
        __slots__ = slots
        __doc__ = help

        def __dir__(self):
            return ["a"]

    C.__name__ = name

    for k, v in properties.items():
        setattr(C, k, property(v))
    for k, v in methods.items():
        setattr(C, k, v)

    return C


def get_function(fun, ctx):
    # if its already a callable: dont change
    if not isinstance(fun, str):
        return fun
    # if no context (parent) is given: get it from globals
    if ctx is None:
        if "." in fun:
            fun = fun.split(".")
            mod, fun = fun[:-1], fun[-1]
            mod = ".".join(mod)
            mod = import_module(mod)
            return getattr(mod, fun)
        else:
            return globals()[fun]
    else:
        return getattr(ctx, fun)


def mk_cnode(
    name,
    function=None,
    index_arg: str = None,
    properties=None,
    pass_ctx=False,
    pass_self=False,
):
    def __init__(self, parent):
        print(f"create {name}")
        self._parent = parent
        self._function = function
        self._name = name
        self._index_arg = index_arg
        self._index_val = None

    def __call__(self, *args, **kwargs):
        ctx = self._parent()

        if self._function:
            f = get_function(self._function, ctx)
            kwargs = kwargs.copy()

            if self._index_arg:
                args = (self._index_val,) + args

            if pass_ctx:
                args = (ctx,) + args

            if pass_self:
                args = (self,) + args

            # print(
            #    f"call {ctx}.{self._name} = {self._function} {args} {kwargs} {self._index_val}"  # noqa
            # )
            ctx = f(*args, **kwargs)

        return ctx

    def __str__(self):
        return self._name

    def __getitem__(self, key):
        print(f"set item: {key}")
        self._index_val = key
        return self

    attributes = [
        "_parent",
        "_module",
        "_function",
        "_name",
        "_index_arg",
        "_index_val",
    ]

    methods = {"__init__": __init__, "__call__": __call__, "__str__": __str__}

    if index_arg:
        methods["__getitem__"] = __getitem__

    properties = properties or {}

    return mk_c(name, attributes, properties, methods, help=f"Help for {name}")


specs = {
    "fun": {"$call": "urllib.parse.quote", "$args": ["string"]},
    "rest": {
        "$call": "load_db",
        "a": {
            "$index": "id_a",
            "list": {"$call": "list"},
            "get": {"$call": "get", "$args": ["id_a"]},
            # "__getitem__": {"$call": "__getitem__"},
            "b": {
                "$index": "id_b",
                "list": {"$call": "list"},
                "get": {"$call": "get"},
            },
        },
    },
}


def do_nothing():
    pass


def get_node_children(obj):
    node = {}
    children = {}
    for k, v in obj.items():
        target = node if k.startswith("$") else children
        target[k] = v
    return node, children


def parse(obj):
    def rec_parse_api_l(obj, name):
        node, children = get_node_children(obj)
        call = node.get("$call")
        index = node.get("$index")
        print(f"init {'node' if children else 'leaf'} {name}: call={call} idx={index}")
        if not children:
            return mk_cnode(name=name, function=call, index_arg=index)
        else:  # node with children
            props = {}
            for cname, child in children.items():
                props[cname] = rec_parse_api_l(child, cname)
            return mk_cnode(name=name, function=call, index_arg=index, properties=props)

    def api_l_main():
        print("ROOT")

    def urljoin(self, parent, *args):
        parts = [x for x in [parent, self._name] if x]
        res = "/".join(parts + [str(x) for x in args])
        print(res)
        return res

    def urlreq(self, parent, *args, **kwargs):
        res = "/".join([parent, self._name])
        return {"url": res}

    def rec_parse_api_r(obj, name):
        node, children = get_node_children(obj)
        index = node.get("$index")
        if not children:
            return mk_cnode(
                name=name,
                function=urlreq,
                index_arg=index,
                pass_ctx=True,
                pass_self=True,
            )
        else:  # node with children
            props = {}
            for cname, child in children.items():
                props[cname] = rec_parse_api_r(child, cname)
            return mk_cnode(
                name=name,
                function=urljoin,
                index_arg=index,
                properties=props,
                pass_ctx=True,
                pass_self=True,
            )

    def api_r_main():
        return None

    return SimpleNamespace(
        api_l=rec_parse_api_l(obj, "MAIN")(api_l_main),
        api_r=rec_parse_api_r(obj, "http://example.com")(api_r_main),
    )

"""
main = parse(specs)

api = main.api_r

res = api.fun("&")
print(res)

res = api.rest.a.list()
print(res)

res = main.api_l.rest.a.get(1).b
print(type(res))

res = main.api_l.rest.a[1].b[2]



api = main.api_l

res = api.fun("&")
assert res == "%26"

res = api.rest.a.list()
assert len(res) == 2

res = api.rest.a.get(1).b.get(2)
assert res.data == "a1b2"

res = api.rest.a[1].b[2]
assert res.data == "a1b2"

res = api.rest.a.get(1)
assert res.data == "a1"

res = api.rest.a[1]
assert res.data == "a1"

"""


db = load_db()


# GET|DEL /db/1/b/1
# NOTE: 
# db[1].b.get(1)
# db[1].b.__getitem__(1)
res = db[1].b[1]  # GET
print(res.data)

# db[1].b.delete(1)
# db[1].b.__delitem__(1)
del db[1].b[1] # DELETE


def fg(n):
    return globals()[n]

def fa(n):
    def f(o, *args, **kwargs):        
        return getattr(o, n)(*args, **kwargs)
    return f

def fga():
    def f(o, *args, **kwargs):        
        getattr(o, *args, **kwargs)
    return f

def fj(*args):
    return '/'.join(str(a) for a in args)

f0 = fg("load_db")
fgi = fa("__getitem__")
fga = getattr


def dl(u, b):
    return ("REQ", b+u)

def d0():
    return "a"

db = f0()
a1 = fgi(db, 1)
b = fga(a1, "b")
b1 = fgi(b, 1)

print(b1)

db = d0()
a1 = fj(db, 1)
b = fj(a1, "b")
b1 = fj(b, 1)

b1 = dl(b1, "http://example.com/")

print(b1)


"""
the python object chain (a.b.c[1].d())
creates a nested object hierarchy, 
each elements has
    * the parent
    * some args+kwargs

after the last element is constructed, call the thing in reverse,
each parent result being the first argument (ctx)

the chain represents a path in the tree of possible calls
"""

def nothing(*args, **kwargs):
    print(f"nothing {args}, {kwargs}")
    pass

class CallChainNode:
    def __init__(self, parent:"CallChainNode"=None, fun=None, args=None, kwargs=None, index_arg=None):
        self.parent = parent
        self.fun = fun or nothing
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.index_arg = index_arg
    
    
    def __call__(self):
        args = self.args
        if self.parent:
            ctx = self.parent()
            args = (ctx,) + args

        print(f'call {args}, {self.kwargs}')
        return self.fun(*args, **self.kwargs)
    
        
    def __getitem__(self, index):
        if not self.index_arg:
            raise Exception("No index")
        self.kwargs[self.index_arg] = index


x = None
for y in [(f0,), (fgi, (1,)), (fga, ("b",)), (fgi, (1,))]:
    x = CallChainNode(x, *y)
res = x()

print(res)


class CallTreeNode:
    
    def __init__(self, parent:CallChainNode=None):
        self.parent=parent
    
def create_property(fun=None, args=None, kwargs=None, index_arg=False):
    def prop(self)-> CallChainNode:
        fun = None
        args = None
        kwargs = None
        index_arg = False
        return CallChainNode(parent=self.parent, fun=fun, args=args, kwargs=kwargs, index_arg=index_arg)
    return property(prop)


setattr(CallTreeNode, "branch_b", create_property())

root = CallTreeNode()


res = root.branch_b()
print(res)