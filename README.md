# Purpose

The purpose of this tool is to create a unified set of api layers
around an existing set of python callables from a json descriptor.

The json descriptor can be validated from a provided json schema file.

The api layers are:

* 1: **api**:
    wrapper functions around exising callables that validate inputs and output and 
    clean documentation

* 2: **server**:
    wsgi server that translates the api to http calls

* 3: **client**:
    python (later: maybe also javascript) client with the same interface as the level 1
    api, that translates the calls into http requests and communicates with layer 2.

* 4: **cli**:
    command line interface that wraps around layer 3 or 1 (because they have the same interface).

The build tool:

* validates the json descriptor
* creates a python package with a module for each of the layers
* creates documentation for the layers
* can run some basic tests provided as examples in the descriptor
* copies a utility module

## Notes

* for the server layer, the (positional) arguments will be translated as part of the url path,
  the (named) options will be translated into the query part

* the (optional) main data input argument as well as the output will be translated into the http body content
  in layer 2 and in (binary) stdin and stdout in layer 4.
  in these transitions, a method to decode / encode the data from and to binary must be specified

* the server layer must:
  * first match the http data (method, path, and expected query args) to an api endpoint
    of matching signature
  * if endpoint has input: read and convert body content
  * convert query args: call the enpoint
  * if output: convert result
  * prepare response
  * send output or []

## Exmaple structure (WIP)

### api.py

```python
"""NOTE: classes are being used as namespaces only,
maybe there is a better way to do that (but not using types.SimpleNamespace)?
"""
from . import utils

def Api(python_paths=None):

    import sys
    sys.path += (python_paths or [])
    import source 
    
    class Api:
        
        @staticmethod
        def example_function(data -> schema, arg1=1) -> int) -> None
            """Documentation

            Args:
                data(schema): 
                arg1(int):
                        
            """
            source.example_function(
                data_source=validate(data),
                arg1=validate(arg1)
            )

        class example_resource:
            def example_get(id -> int, arg1=1) -> int) -> schema
            """Documentation

            Args:
                id(int)
            
            Returns:
                schema
            """
            return validate(
                source.resource.get(
                    id=validate(id),
                    arg1=validate(arg1)
                )
            )


    return Api

```

### server.py

```python
from . import utils
from .api import Api


def router(method, path, ...):
    api = Api()

    api.example_resource.get()


    # TODO: don't actually use if/elifs in code
    if (method, path) == ("POST", "/example_function"):
        return api.example_function
    elif (method, path) == ("GET", "/resource"):
        return api.example_resource.get

    # PATH + url + query -> api::callable

    def handle(callable, output_encode=None):
        result = callable(**argugments)
        if output_encode:
            result = output_encode(result)
        else:
            result = b''




    return callable

# wsgi entry
application = utils.create_wsgi_application(router)

if __name__ == '__main__':
    utils.start_wsgi_server(application, port=8000)
```

### client.py

```python
"""NOTE: classes are being used as namespaces only,
maybe there is a better way to do that (but not using types.SimpleNamespace)?
"""
from . import utils
def Api(host):
    
    class Api:
        
        @staticmethod
        def example_function(data -> schema, arg1=1) -> int) -> None
            """Documentation

            Args:
                data(schema): 
                arg1(int):
                        
            """
            url, method = get_url(host, 'example_function')
            response = requests.request(method=method, url=url, data=data, params={"arg1": arg1})


        class example_resource:
            def example_get(id -> int, arg1=1) -> int) -> schema
            """Documentation

            Args:
                id(int)
            
            Returns:
                schema
            """
            url, method = get_url(host, 'resource.example_get', id)
            response = requests.request(method=method, url=url, params={"arg1": arg1})
            return decode(response.content)


    return Api

```


### cli.py

```python
from . import utils
from .api import Api as ApiLocal
from .client import Api as ApiRemote

@click.group()
@main.option("--host", default=None)
def main(ctx, host):
    if host:
        api = ApiRemote(host)
    else:
        api = ApiLocal()
    ctx.obj["api"] = api

@main.command("example_function")
@main.option("--arg1", default=1, help="")
def main_example_function(ctx, arg1):
    data = utils.decode(stdin.read())
    ctx.obj["api"].example_function(
        data=data,
        arg1=arg1
    )    


if __name__ == "__main__":
    main()

```
