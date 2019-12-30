# -*- encoding: utf-8 -*-
"""The webserver entrypoint."""

from asyncio import AbstractEventLoop, get_event_loop
import typing as T

from aiohttp import web

from kofi.config import read_config
from kofi.log import setup_log
from kofi.routes import generate_app_routes


def setup(
    config: T.Dict[T.Text, T.Any], loop: T.Optional[AbstractEventLoop] = None
) -> web.Application:
    """
    Setup the application.
    """
    if loop is None:
        loop = get_event_loop()
    app = web.Application(loop=loop)
    app["config"] = config
    app["log"] = setup_log(config["log"])
    app.add_routes(generate_app_routes(config))
    return app


def start(app: web.Application) -> None:
    """
    Start the application.
    """
    web.run_app(app, host=app["config"]["host"], port=app["config"]["port"])


def run() -> None:
    """KoFi entrypoint."""
    config = read_config()
    app = setup(config)
    start(app)


def run_from_shell(config: T.Dict[T.Text, T.Any]) -> None:
    """KoFi shell entrypoint."""
    app = setup(config)
    start(app)
