
class api:
    
    def get(arg1: int=None, arg2: str=None) -> str:
        """Example description
        multiline text
        Args:
            arg1(int)
            arg2(str)
        Returns:
            str
        """
        request(
            "GET",
            "get",
            params={"arg1": arg1, "arg2": arg2},
            data=None
        )
    
    class module:
        
        class submodule:
            
            def post(data: float, arg3: str=1, arg4: float=None) -> bool:
                """bla b
                Args:
                    data(float)
                    arg3(str): blabla text arg3 Defaults to 1
                    arg4(float)
                Returns:
                    bool
                """
                request(
                    "POST",
                    "module/submodule/post",
                    params={"arg3": arg3, "arg4": arg4},
                    data=encode(data)
                )
    
    class rest:
        
        class resource:
            
            def list() -> int:
                """None
                Returns:
                    int
                """
                request(
                    "GET",
                    "rest/resource",
                    params={},
                    data=None
                )
            
            def post(data: int) -> int:
                """None
                Args:
                    data(int)
                Returns:
                    int
                """
                request(
                    "POST",
                    "rest/resource",
                    params={},
                    data=encode(data)
                )
            
            def get(pk: int) -> int:
                """None
                Args:
                    pk(int)
                Returns:
                    int
                """
                request(
                    "GET",
                    "rest/resource/%s" % (pk),
                    params={},
                    data=None
                )
            
            def delete(pk: int) -> None:
                """None
                Args:
                    pk(int)
                """
                request(
                    "DELETE",
                    "rest/resource/%s" % (pk),
                    params={},
                    data=None
                )
            
            def put(data: int, pk: int) -> None:
                """None
                Args:
                    data(int)
                    pk(int)
                """
                request(
                    "PUT",
                    "rest/resource/%s" % (pk),
                    params={},
                    data=encode(data)
                )
            
            def patch(data: bool, pk: int) -> None:
                """None
                Args:
                    data(bool)
                    pk(int)
                """
                request(
                    "PATCH",
                    "rest/resource/%s" % (pk),
                    params={},
                    data=encode(data)
                )