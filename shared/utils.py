import functools


def start_wsgi_server(application, port):
    pass

def create_wsgi_application(router):
    def application():
        pass

    return application

def validate(data, schema):
    return data


def dec(fun):
    @functools.wraps(fun)
    def fun2(*args, **kwargs):
        return fun(*args, **kwargs) + 1
    return fun2

