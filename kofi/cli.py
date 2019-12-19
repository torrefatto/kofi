# -*- encoding: utf-8 -*-
"""Console script for kofi."""
import sys
from pprint import pformat
import typing as T

import click

from kofi.config import read_config, merge_configs
from kofi.main import run_from_shell


@click.command()
@click.option("-c", "--config", "config_path", help="The path to the config file.")
@click.option("-b", "--bind-address", "host", help="The address to bind kofi to.")
@click.option("-p", "--port", "port", help="The port to bind kofi to.")
@click.option(
    "-l",
    "--log-level",
    "log_level",
    help="The log level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
)
@click.option("--syslog", is_flag=True)
@click.option("--log-file", "log_file", type=click.Path(exists=True))
def main(
    config_path: T.Optional[T.Text],
    host: T.Text,
    port: int,
    log_level: T.Text,
    syslog: bool,
    log_file: T.Optional[T.Text],
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
    config = read_config(config_path)
    def_config = merge_configs(config, shell_config)

    if log_level and log_level.upper() == "DEBUG":
        click.echo("Resulting conf:\n{}".format(pformat(def_config)))

    run_from_shell(def_config)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
