class Type():
    def __init__(self, type):            
        self.type = type
    
    @property
    def python_type_annotation(self):
        return ({
            "null": "None",
            "boolean": "bool",
            "string": "str",
            "number": "float",
            "integer": "int",
            "bytes": "bytes",
            "array": "list",
        })[self.type]
    
    @property
    def python_repr(self):
        return ({
            "boolean": "Type",
            "string": "Type",
            "number": "Type",
            "integer": "Type",
            "bytes": "Type",
            "array": "Type"
        })[self.type]
    
    @property
    def click_repr(self):
        return ({
            "boolean": "bool",
            "string": "str",
            "number": "float",
            "integer": "int",
            "bytes": "bytes",            
        })[self.type]