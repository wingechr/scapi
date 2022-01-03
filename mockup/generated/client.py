import logging
import utils

__version__ = "0.1.0"


def api(remote="http://localhost:8000"):
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
                return utils.decode_content(
                    utils.request(
                        method="POST",
                        url="%s/mod/fun/%s" % (remote, b),
                        params={"c": c, "d": d},
                        data=utils.encode_content(data, None),
                    ),
                    "output_schema",
                )

    return api
