# -*- encoding: utf-8 -*-
"""The webserver entrypoint."""

from aiohttp import web
import typing as T

from kofi.config import read_config
from kofi.routes import app_routes


def setup(config: T.Dict[T.Text, T.Any]) -> web.Application:
    """
    Setup the application.
    """
    app = web.Application()
    app["config"] = config
    app.add_routes(app_routes)
    return app


def start(app: web.Application) -> None:
    """
    Start the application.
    """
    web.run_app(app, host=app["config"]["host"], port=app["config"]["port"])


def main() -> None:
    """KoFi entrypoint."""
    config = read_config()
    app = setup(config)
    start(app)
