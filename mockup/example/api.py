from . import utils
import logging
import sys

def Api(python_paths=None):
    sys.path += (python_paths or [])
    import package.module
    import package.rest
    import package.submodule.module
    class Api:
        @staticmethod
        def get(arg1: str=None, arg2: str=None) -> str:
            """Example description
            multiline text

            Args:
                arg1(str):
                    default: None

                arg2(str):
                    default: None


            Returns:
                str: TODO output description

            """
            return utils.validate(
                package.module.get(
                    arg1=utils.validate(arg1, str),
                    arg2=utils.validate(arg2, str)
                ),
                str
            )

        class module:
            class submodule:
                @staticmethod
                def post(data, arg3: str=1, arg4: str=None) -> str:
                    """bla b

                    Args:
                        data:

                        arg3(str): blabla text arg3
                            default: 1

                        arg4(str):
                            default: None


                    Returns:
                        str: TODO output description

                    """
                    return utils.validate(
                        package.submodule.module.post(
                            data_orig=utils.validate(data, None),
                            arg3=utils.validate(arg3, str),
                            arg4_orig=utils.validate(arg4, str)
                        ),
                        str
                    )



        class rest:
            class resource:
                @staticmethod
                def list() -> str:
                    """

                    Returns:
                        str: TODO output description

                    """
                    return utils.validate(
                        package.rest.Resources.Resource.list(
                        ),
                        str
                    )

                @staticmethod
                def post(data) -> str:
                    """

                    Args:
                        data:


                    Returns:
                        str: TODO output description

                    """
                    return utils.validate(
                        package.rest.Resources.Resource.post(
                            data=utils.validate(data, None)
                        ),
                        str
                    )

                @staticmethod
                def get(id) -> str:
                    """

                    Args:
                        id:


                    Returns:
                        str: TODO output description

                    """
                    return utils.validate(
                        package.rest.Resources.Resource.get(
                            id=utils.validate(id, None)
                        ),
                        str
                    )

                @staticmethod
                def delete(id) -> None:
                    """

                    Args:
                        id:


                    """
                    package.rest.Resources.Resource.delete(
                        id=utils.validate(id, None)
                    ),

                @staticmethod
                def put(id, data) -> None:
                    """

                    Args:
                        id:

                        data:


                    """
                    package.rest.Resources.Resource.put(
                        id=utils.validate(id, None),
                        data=utils.validate(data, None)
                    ),

                @staticmethod
                def patch(id, data) -> None:
                    """

                    Args:
                        id:

                        data:


                    """
                    package.rest.Resources.Resource.patch(
                        id=utils.validate(id, None),
                        data=utils.validate(data, None)
                    ),




    return Api
