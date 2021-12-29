import logging
from types import SimpleNamespace


def api(**_kwargs):
    logging.debug("loading api")

    '''{{imports}}'''
    
    def validate(fun):
        def _fun(*args, **kwargs):
            logging.debug('validate input')
            res = fun(*args, **kwargs)
            logging.debug('validate output')
            return res
        return _fun

    return '''{{api_namespaces}}'''