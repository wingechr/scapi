import package.module
import package.rest
import package.submodule.module

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
        return Type.validate(
            package.module.get(
                arg1=Type.validate(arg1),
                arg2=Type.validate(arg2)
            )
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
                return Type.validate(
                    package.submodule.module.post(
                        data_orig=Type.validate(data),
                        arg3=Type.validate(arg3),
                        arg4_orig=Type.validate(arg4)
                    )
                )
    
    class rest:
        
        class resource:
            
            def list() -> int:
                """None
                Returns:
                    int
                """
                return Type.validate(
                    package.rest.Resources.Resource.list(
                    )
                )
            
            def post(data: int) -> int:
                """None
                Args:
                    data(int)
                Returns:
                    int
                """
                return Type.validate(
                    package.rest.Resources.Resource.post(
                        data=Type.validate(data)
                    )
                )
            
            def get(pk: int) -> int:
                """None
                Args:
                    pk(int)
                Returns:
                    int
                """
                return Type.validate(
                    package.rest.Resources.Resource.get(
                        pk=Type.validate(pk)
                    )
                )
            
            def delete(pk: int) -> None:
                """None
                Args:
                    pk(int)
                """
                package.rest.Resources.Resource.delete(
                    pk=Type.validate(pk)
                )
            
            def put(data: int, pk: int) -> None:
                """None
                Args:
                    data(int)
                    pk(int)
                """
                package.rest.Resources.Resource.put(
                    data=Type.validate(data),
                    pk=Type.validate(pk)
                )
            
            def patch(data: bool, pk: int) -> None:
                """None
                Args:
                    data(bool)
                    pk(int)
                """
                package.rest.Resources.Resource.patch(
                    data=Type.validate(data),
                    pk=Type.validate(pk)
                )