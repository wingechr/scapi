import logging
import utils

application = utils.WSGIHandler(utils.get_api())


@application.route("POST", ["^mod$", "^fun$", "^(?P<b>.*)$"], "data")
def route_mod_fun(data: bytes, b: list, c: list = None, d: list = None) -> bytes:
    return utils.encode(
        application.api.mod.fun(
            data=utils.decode(data),
            b=utils.convert(b),
            c=utils.convert(c),
            d=utils.convert(d),
        )
    )


if __name__ == "__main__":
    utils.wsgi_serve(__file__)
