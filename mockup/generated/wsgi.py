import logging
import utils

__version__ = "0.1.0"

application = utils.WSGIHandler(utils.get_api())


@application.route("POST", ["mod", "fun", "(?P<b>.+)"], "data")
def route_mod_fun(data: object, b: int, c: bool = None, d: list = None) -> object:
    return utils.encode_content(
        application.api.mod.fun(
            data=utils.decode_content(data, None),
            b=utils.from_string(b, "integer"),
            c=utils.single_from_string_list(c, "boolean"),
            d=utils.list_from_string_list(d, "integer"),
        ),
        "output_schema",
    )


if __name__ == "__main__":
    utils.wsgi_serve(__file__)
