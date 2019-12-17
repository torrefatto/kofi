# -*- encoding: utf-8 -*-
"""The webserver entrypoint."""

from aiohttp import web
import typing as T

from kofi.config import read_config
from kofi.log import setup_log
from kofi.routes import app_routes


def setup(config: T.Dict[T.Text, T.Any]) -> web.Application:
    """
    Setup the application.
    """
    app = web.Application()
    app["config"] = config
    print(f"CONFIG: {config}")
    app["log"] = setup_log(config["log"])
    print("Log registered")
    app.add_routes(app_routes)
    print(f"Routes added: {app_routes}")
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


if __name__ == "__main__":
    main()
