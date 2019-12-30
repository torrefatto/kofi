# -*- encoding: utf-8 -*-
"""
Read and validate the config.
"""

from ipaddress import IPv4Address, IPv6Address, AddressValueError
import os
import pathlib
import re
import typing as T

import yaml


def merge_configs(
    config: T.Dict[T.Text, T.Any], shell_config: T.Dict[T.Text, T.Any]
) -> T.Dict[T.Text, T.Any]:
    """
    Merge the configuration from file with the one from command
    line parameters, favouring the latter.
    """
    out_config = {}
    for key, val in config.items():
        if key != "log":
            out_config[key] = shell_config.get(key, config.get(key))
    out_config["log"] = {}
    if "log" in shell_config:
        for key, val in config["log"].items():
            out_config["log"][key] = shell_config["log"].get(
                key, config["log"].get(key)
            )
    else:
        out_config["log"] = config["log"]

    return out_config


def read_config(conf_file: T.Optional[T.Text] = None) -> T.Dict[T.Text, T.Any]:
    """
    Find the configuration file and parse it.
    """
    if conf_file is None:
        conf_file = _find_conf()
    if conf_file:
        with open(conf_file) as f:
            conf = yaml.safe_load(f)

        out_conf = {}
        for conf_k, conf_v in DEFAULT.items():
            out_conf[conf_k] = _validate(conf_k, conf.get(conf_k), conf_v)
    else:
        out_conf = DEFAULT

    return out_conf


def _find_conf() -> T.Text:
    for conf_path in DEFAULT_CONF_PATH:
        if os.path.exists(conf_path):
            return conf_path

    return ""


def _validate(key: T.Text, datum: T.Any, default: T.Any) -> T.Any:
    if datum is not None:
        return VALIDATE[key](datum)  # type: ignore
    return default


def _validate_host(host: T.Text) -> T.Text:
    if host.lower() == "localhost":
        return host
    try:
        IPv4Address(host)
        return host
    except AddressValueError:
        try:
            IPv6Address(host)
            return host
        except AddressValueError:
            raise ValueError(f"'host' is invalid in configuration: {host}")


def _validate_port(port: int) -> int:
    if 0 < port and port < 65535:
        return port

    raise ValueError(f"'port' is invalid in configuration: {port}")


def _validate_log(log_conf: T.Dict[T.Text, T.Any]) -> T.Dict[T.Text, T.Any]:
    log_level = log_conf.get("level", DEFAULT_LOG_CONF["level"]).upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        raise ValueError(
            f"'level' is invalid in configuration: {log_level}\
                Allowed values are ('DEBUG', 'INFO', 'WARNING', 'ERROR')"
        )
    syslog = log_conf.get("syslog", DEFAULT_LOG_CONF["syslog"])
    if not isinstance(syslog, bool):
        raise ValueError(
            f"'syslog' is invalid in configuration: {syslog}\
                Allowed values are ('true', 'false')"
        )
    conf = {"level": log_level, "syslog": syslog}
    log_file = log_conf.get("log_file")
    if log_file:
        if not os.path.exists(os.path.dirname(log_file)):
            raise ValueError(
                f"'log_file' is invalid in configuration: {log_file}\
                    Base directory does not exist."
            )
        conf["log_file"] = log_file

    return conf


def _validate_graphiql(graphiql_conf: T.Optional[bool]) -> bool:
    if graphiql_conf is None:
        return False
    if isinstance(graphiql_conf, bool):
        return graphiql_conf
    raise ValueError(f"'graphiql' is invalid in configuration: {graphiql_conf}")


DEFAULT_CONF_PATH = [
    os.path.join(os.path.curdir, "kofi.yml"),
    os.path.join(pathlib.Path.home(), "kofi.yml"),
    "/etc/kofi/kofi.yml",
]

DEFAULT_LOG_CONF = {"level": "ERROR", "syslog": False}
DEFAULT = {"host": "0.0.0.0", "port": 1312, "log": DEFAULT_LOG_CONF, "graphiql": False}

VALIDATE = {
    "host": _validate_host,
    "port": _validate_port,
    "log": _validate_log,
    "graphiql": _validate_graphiql,
}
