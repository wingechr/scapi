# Purpose

The purpose of this tool is to create a unified set of api layers
around an existing set of python sources from a json descriptor.

The json descriptor can be validated from a provided json schema file.

The api layers are:

- 1: **api**:
  wrapper functions around exising sources that validate inputs and output and
  clean documentation

- 2: **wsgi**:
  wsgi script that translates the api to http calls

- 3: **client**:
  python (later: maybe also javascript) client with the same interface as the level 1
  api, that translates the calls into http requests and communicates with layer 2.

- 4: **cli**:
  command line interface that wraps around layer 3 or 1 (because they have the same interface).

The build tool:

- validates the json descriptor
- creates a python package with a module for each of the layers
- creates documentation for the layers
- can run some basic tests provided as examples in the descriptor
- copies a utility module

## Notes

- for the server layer, the (positional) arguments will be translated as part of the url path,
  the (named) options will be translated into the query part

- the (optional) main data input argument as well as the output will be translated into the http body content
  in layer 2 and in (binary) stdin and stdout in layer 4.
  in these transitions, a method to decode / encode the data from and to binary must be specified

- the server layer must:

  - first match the http data (method, path, and expected query args) to an api endpoint
    of matching signature
  - if endpoint has input: read and convert body content
  - convert query args: call the enpoint
  - if output: convert result
  - prepare response
  - send output or []

- types:
  - click.STRING string str
  - click.BOOL boolean bool
  - click.INT integer int
  - click.FLOAT number float
  - multiple=True array list
  - bytes

## Build example

```
SET PYTHONPATH=test/example
python -m scapi test/example/example_schema.json dist/example -d -t
```
