# from functools import partial
import logging
from importlib import import_module
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Type, Union
from urllib.parse import quote


def get_function_from_str(fun: str) -> object:
    """get method from module or globals"""
    if "." in fun:
        fun = fun.split(".")
        mod, fun = fun[:-1], fun[-1]
        mod = ".".join(mod)
        mod = import_module(mod)
        return getattr(mod, fun)
    else:
        return globals()[fun]


def create_callback(
    use_ctx: bool = None,
    fun: str = None,
    arg_names: List[str] = None,
    kwarg_names: Dict[str, str] = None,
    args=None,
    kwargs=None,
) -> Callable:
    is_prop = arg_names is None and kwarg_names is None

    if not fun:
        # structural dummy node
        def fun_on_callback(ctx):
            return ctx

    elif not use_ctx:
        # new context from external
        def fun_on_callback(_ctx):
            # return external object as new context
            return get_function_from_str(fun)

    elif is_prop:

        def fun_on_callback(ctx):
            return getattr(ctx, fun)

    else:
        # map kwargs: TODO
        args = args or ()
        kwargs = kwargs or {}
        assert len(args) == len(arg_names or ())
        kwargs = dict((kwarg_names[k], v) for k, v in kwargs.items())

        # callcontext
        def fun_on_callback(ctx):
            return getattr(ctx, fun)(*args, **kwargs)

    return fun_on_callback


class CallChainNode:
    """
    A subclass of this represents a node in the api TREE,
    with different methods (__call__,__getitem__,@property) as possible branches
    each of these methods, when called created an instance
    An instance of this class represents a node in the actuall call chain.
    but still, this does not call any of the underlying methods.
    this will only be done when calling the callback() method, with will
    recursively co back in the tree and
        * get context as result of parent.callback()
        * applying the bound function over the context
        *

    """

    def __init__(self, fun=None, parent: "CallChainNode" = None):
        print(f"init {fun}")
        self.parent = parent
        self.fun_on_callback = fun  # or pass_ctx

    def __str__(self):
        return self.__class__.__name__

    def _callback(self):
        print(f"calling {self}")
        if self.parent:
            ctx = self.parent._callback()
        else:  # root / recursion end
            ctx = None

        if self.fun_on_callback:
            ctx = self.fun_on_callback(ctx)

        return ctx


def create_attr(
    result_cls: Type[CallChainNode] = None,
    use_ctx: bool = None,
    fun: str = None,
    arg_names: List[str] = None,
    kwarg_names: Dict[str, str] = None,
) -> object:
    is_prop = arg_names is None and kwarg_names is None
    is_callable = fun and use_ctx and not is_prop

    def attr(self, *args, **kwargs) -> Union[CallChainNode, Any]:
        fun_on_callback = create_callback(
            use_ctx=use_ctx,
            fun=fun,
            arg_names=arg_names,
            kwarg_names=kwarg_names,
            args=args,
            kwargs=kwargs,
        )

        if result_cls is None:
            result = CallChainNode(parent=self, fun=fun_on_callback)
        else:
            result = result_cls(parent=self, fun=fun_on_callback)

        is_final = result_cls is None

        if is_final:
            if not is_callable:
                logging.warning("last node should be a callable")
            result = result._callback()

        return result

    if is_prop:
        attr = property(attr)

    return attr


def create_node_class(
    attrs: Dict[str, dict], clsname: str = None
) -> Type[CallChainNode]:
    class C(CallChainNode):
        __slots__ = list(attrs)

    if not attrs:
        raise Exception("No branches")

    for name, attr in attrs.items():
        if isinstance(attr, dict):
            attr = create_attr(**attr)
        setattr(C, name, attr)

    if clsname:
        C.__name__ = clsname

    return C


# Helper


def create_fun_cls(fun, *arg_names, **kwarg_names):
    return create_node_class(
        {
            fun: dict(
                use_ctx=True,
                fun=fun,
                arg_names=arg_names,
                kwarg_names=kwarg_names,
            )
        }
    )


def create_attr_ext_fun_call(fun, *arg_names, **kwarg_names):
    return create_attr(
        result_cls=create_fun_cls("__call__", *arg_names, **kwarg_names),
        use_ctx=False,
        fun=fun,
    )


def create_attr_ext_index_obj(fun, key_arg):
    return create_attr(
        result_cls=create_fun_cls("__getitem__", key_arg),
        use_ctx=False,
        fun=fun,
    )


def create_attr_index_obj(key_arg):
    return create_attr(result_cls=create_fun_cls("__getitem__", key_arg), use_ctx=True)


# TEST


def test_fun_sum(x):
    return x + 1


assert get_function_from_str("test_fun_sum")(1) == 2
assert get_function_from_str("urllib.parse.quote")("&") == "%26"


ns = SimpleNamespace(x=9)

# function
setts = dict(use_ctx=True, fun="__call__", arg_names=["string"])
f = create_callback(**setts, args=["&"])
assert f(quote) == "%26"

# use a root callback
o = create_node_class({"n1": setts})(lambda _ctx: quote)
assert o.n1("&") == "%26"

# prop

setts = dict(use_ctx=True, fun="x")
p = create_callback(setts)(ns)
assert p.x == 9

o = create_node_class({"x": setts})(lambda _ctx: ns)
assert o.x == 9

# external func

setts = dict(use_ctx=False, fun="urllib.parse.quote")
f = create_callback(**setts)(None)
assert f("&") == "%26"
o = create_node_class({"q": setts})()
assert o.q("&") == "%26"

# dummy

setts = dict(use_ctx=False, fun=None)
d = create_callback(**setts)("A")
assert d == "A"
o = create_node_class({"a": setts})()
assert o.a is None


CLS = create_node_class({"f": create_attr_ext_fun_call("urllib.parse.quote", "string")})
o = CLS()
assert o.f("&") == "%26"

DATA = {"a": 1}

CLS = create_node_class({"f": create_attr_ext_index_obj("DATA", "key")})
o = CLS()
assert o.f["a"] == 1


CLS = create_node_class({"f": create_attr_index_obj("key")})
o = CLS(lambda _: DATA)
assert o.f["a"] == 1
