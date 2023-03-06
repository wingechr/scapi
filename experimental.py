import urllib.parse  # noqa
from importlib import import_module
from types import SimpleNamespace
from urllib.parse import quote_plus  # noqa

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

    def get(self, id):
        return self.instances[id]

    def __getitem__(self, id):
        return self.get(id)

    def delete(self, id):
        del self.instances[id]

    def create(self, data):
        inst = self.cls(data)
        id = (max(self.instances.keys()) if self.instances else 0) + 1
        inst.id = id
        assert id not in self.instances
        self.instances[id] = inst
        return inst

    def replace(self, id, data):
        inst = self.cls(data)
        inst.id = id
        self.instances[id] = inst

    def update(self, id, data):
        inst = self.instances[id]
        inst.data.update(data)
        return inst

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


main = parse(specs)

api = main.api_r

res = api.fun("&")
print(res)

res = api.rest.a.list()
print(res)

res = main.api_l.rest.a.get(1).b
print(type(res))

res = main.api_l.rest.a[1].b[2]


"""
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
