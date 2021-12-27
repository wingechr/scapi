import logging

LOGGING_DATE_FMT = '%Y-%m-%d %H:%M:%S'
LOGGING_FMT = "[%(asctime)s %(levelname)7s] %(message)s"

logging.basicConfig(format=LOGGING_FMT, datefmt=LOGGING_DATE_FMT, level=logging.DEBUG)

import sys
import re
import os
import inspect

# environment for imports
sys.path.append(os.path.dirname(__file__) + '/../0_code')
import package

def validate(fun):
    def _fun(*args, **kwargs):
        logging.info('validate input')
        res = fun(*args, **kwargs)
        logging.info('validate output')
        return res
    return _fun


from types import SimpleNamespace
api = SimpleNamespace(
module = SimpleNamespace(
    get=validate(package.module.get),
    post=validate(package.submodule.module.post)
),
resource = SimpleNamespace(
    get=validate(package.rest.Resources.Resource.get),
    post=validate(package.rest.Resources.Resource.post),
    put=validate(package.rest.Resources.Resource.put),
    patch=validate(package.rest.Resources.Resource.patch),
    list=validate(package.rest.Resources.Resource.list),
    delete=validate(package.rest.Resources.Resource.delete)
)
)




#for path, callable in callables.items():
#    sig = inspect.signature(callable)
    #print(callable.__doc__ or "")
    #print(callable.__annotations__.get("return"))
    #for param in sig.parameters.values():
    #    print(param.name, param.default, param.annotation if not param.annotation == inspect._empty else "")
    
    #print(inspect.cleandoc(inspect.getdoc(callable)))
    #print(inspect.cleandoc(inspect.getdoc(callable)))
    #print(inspect.getmodule(callable).__name__)

#    callable()


# TODO
# * argument mapped to data/body (argument annotation?)
# * argument(s) mapped to path (argument annotation?)
# * http method (infer?)
# * prefix hierarchy
# * name (callable.__name__)
#

#print(package.__dict__.keys())
#print(package.rest.__dict__.keys())
#print(package.rest.Resource.__dict__.keys())
#print(package.rest.Resource.get.__dict__.keys())


#print(package.module.get.__dict__.keys())


#print(p.rest.Resource.get.__module__)