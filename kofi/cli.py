# -*- encoding: utf-8 -*-
"""Console script for kofi."""
import sys
from pprint import pformat
import typing as T

import click

from kofi.config import read_config, merge_configs, VALIDATE
from kofi.main import run_from_shell


def _validate(ctx: click.Context, param: T.Text, value: T.Any) -> None:
    if value is not None:
        try:
            VALIDATE[param](value)  # type: ignore
        except ValueError as e:
            raise click.BadParameter(str(e))


def _validate_host(ctx, param, value):
    _validate(ctx, "host", value)


def _validate_port(ctx, param, value):
    _validate(ctx, "port", value)


@click.command()
@click.option("-c", "--config", "config_path", help="The path to the config file.")
@click.option(
    "-b",
    "--bind-address",
    "host",
    help="The address to bind kofi to.",
    callback=_validate_host,
)
@click.option(
    "-p",
    "--port",
    "port",
    type=click.INT,
    help="The port to bind kofi to.",
    callback=_validate_port,
)
@click.option(
    "-l",
    "--log-level",
    "log_level",
    help="The log level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
)
@click.option("--syslog", help="Send the log also to the syslog", is_flag=True)
@click.option(
    "--log-file",
    "log_file",
    help="Send the log also to file",
    type=click.Path(exists=True),
)
@click.option(
    "--graphiql", "graphiql", help="Enable the graphiql facility", is_flag=True
)
@click.pass_context
def main(
    ctx: click.Context,
    config_path: T.Optional[T.Text],
    host: T.Text,
    port: int,
    log_level: T.Text,
    syslog: bool,
    log_file: T.Optional[T.Text],
    graphiql: bool,
):
    """Console script for kofi."""
    shell_config = {}  # type: T.Dict[T.Text, T.Any]
    if host:
        shell_config["host"] = host
    if port:
        shell_config["port"] = port
    log_conf = {
        "level": log_level,
        "syslog": syslog,
    }
    if log_file:
        log_conf["log_file"] = log_file
    if log_level or syslog or log_file:
        shell_config["log"] = log_conf
    if graphiql:
        shell_config["graphiql"] = True
    config = read_config(config_path)
    def_config = merge_configs(config, shell_config)

    if log_level and log_level.upper() == "DEBUG":
        click.echo("Resulting conf:\n{}".format(pformat(def_config)))

    run_from_shell(def_config)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
