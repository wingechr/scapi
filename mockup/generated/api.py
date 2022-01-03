import logging
import utils

__version__ = "0.1.0"


def api():

    import code

    class api:
        class mod:
            @staticmethod
            def fun(data: object, b: int, c: bool = None, d: list = None) -> object:
                """Example description
                multiline text

                Args:
                    data(object): desc
                    b(int): description
                    c(bool): desc
                    d(list): desc

                Returns:
                    object: desc
                """
                return utils.validate_content(
                    code.fun(
                        a=utils.validate_content(data, None),
                        b=utils.validate(b, "integer"),
                        c=utils.validate(c, "boolean"),
                        d=utils.validate(d, "integer"),
                    ),
                    "output_schema",
                )

    return api
