import logging
import utils

__version__ = "0.1.0"


def api():

    # we put the imports inside the function so we don't import it when it's remote
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
                    d(list): List of int. desc

                Returns:
                    object: desc
                """
                return utils.validate_content(
                    code.fun(
                        a=utils.validate_content(
                            data, "application/json; charset=utf8; schema="
                        ),
                        b=utils.validate(b, {"type": "integer"}),
                        c=utils.validate(c, {"type": "boolean"}),
                        d=utils.validate(
                            d, {"type": "array", "items": {"type": "integer"}}
                        ),
                    ),
                    "application/json; charset=utf8; schema=output_schema",
                )

    return api
