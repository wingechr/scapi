from .utils import logging

class Resources:
    
    class Resource:

        @classmethod
        def list(cls, arg5:None=None, arg6:None=None) -> None:
            """list docstring
            """        
            logging.debug("rest.resource.list(arg5=%s, arg6=%s)", arg5, arg6)
            return {
                "arg5": arg5,
                "arg6": arg6
            }

        @classmethod
        def post(cls, data:None=None) -> None:
            """post docstring
            """
            logging.debug("rest.resource.post(data=%s)", data)
            return {
                "data": data
            }

        @classmethod
        def get(cls, id:None=None, arg7:None=None) -> None:
            """get docstring
            """
            logging.debug("rest.resource.get(id=%s, arg7=%s)", id, arg7)
            return {
                "id": id,
                "arg7": arg7
            }

        @classmethod
        def delete(cls, id:None=None) -> None:
            """delete docstring
            """
            logging.debug("rest.resource.delete(id=%s)", id)
            return {
                "id": id
            }

        @classmethod
        def put(cls, id:None=None, data:None=None) -> None:
            """put docstring
            """
            logging.debug("rest.resource.put(id=%s, data=%s)", id, data)
            return {
                "id": id,
                "data": data
            }

        @classmethod
        def patch(cls, id:None=None, data:None=None) -> None:
            """patch docstring
            """
            logging.debug("rest.resource.patch(id=%s, data=%s)", id, data)
            return {
                "id": id,
                "data": data
            }