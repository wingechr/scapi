import logging
from types import SimpleNamespace


def api(**_kwargs):
    logging.debug("loading api")

    import package.module
    import package.rest
    import package.submodule.module
    
    def validate(fun):
        def _fun(*args, **kwargs):
            logging.debug('validate input')
            res = fun(*args, **kwargs)
            logging.debug('validate output')
            return res
        return _fun

    return SimpleNamespace(
        module=SimpleNamespace(
            submodule=SimpleNamespace(
                get=validate(package.module.get),
                post=validate(package.submodule.module.post)
            )
        ),
        rest=SimpleNamespace(
            resource=SimpleNamespace(
                delete=validate(package.rest.Resources.Resource.delete),
                get=validate(package.rest.Resources.Resource.get),
                list=validate(package.rest.Resources.Resource.list),
                patch=validate(package.rest.Resources.Resource.patch),
                post=validate(package.rest.Resources.Resource.post),
                put=validate(package.rest.Resources.Resource.put)
            )
        )
    )