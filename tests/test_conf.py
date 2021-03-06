# -*- encoding: utf-8 -*-
"""Tests for the configuration parser"""

import os
import py  # type: ignore
import typing as T
from unittest import mock

import yaml
import pytest

from kofi.config import read_config, merge_configs, DEFAULT_LOG_CONF


def fill_mock_conf(conf: T.Dict[T.Text, T.Any], tmpdir: py.path.local) -> T.Text:
    base_dir = tmpdir.mkdir("conf")
    conf_path = base_dir.join("kofi.yml")
    with open(conf_path, "w") as f:
        f.write(yaml.dump(conf))

    return conf_path


@pytest.mark.parametrize(
    "file_conf,shell_conf,result",
    [
        [
            {"host": "1.3.1.2", "port": 1312, "log": {}, "graphiql": True},
            {"host": "localhost", "port": 1000, "graphiql": False},
            {"host": "localhost", "port": 1000, "log": {}, "graphiql": False},
        ],
        [
            {
                "host": "1.3.1.2",
                "port": 1312,
                "log": {"syslog": True, "log_file": "/tmp/kofi.log"},
                "graphiql": False,
            },
            {"port": 1000, "log": {"syslog": False}, "graphiql": True},
            {
                "host": "1.3.1.2",
                "port": 1000,
                "log": {"syslog": False, "log_file": "/tmp/kofi.log"},
                "graphiql": True,
            },
        ],
    ],
)
def test_merge_conf(
    file_conf: T.Dict[T.Text, T.Any],
    shell_conf: T.Dict[T.Text, T.Any],
    result: T.Dict[T.Text, T.Any],
) -> None:
    """Tests merge_configs in various cases."""
    assert result == merge_configs(file_conf, shell_conf)


@pytest.mark.parametrize(
    "conf_data, result",
    [
        [
            {
                "host": "127.0.0.1",
                "port": 13121,
                "log": {"level": "DEBUG", "syslog": True, "log_file": "/tmp/logfile",},
                "graphiql": True,
            },
            {
                "host": "127.0.0.1",
                "port": 13121,
                "log": {"level": "DEBUG", "syslog": True, "log_file": "/tmp/logfile",},
                "graphiql": True,
            },
        ],
        [
            {"host": "127.0.0.1", "log": {"syslog": True}},
            {
                "host": "127.0.0.1",
                "port": 1312,
                "log": {"level": "ERROR", "syslog": True},
                "graphiql": False,
            },
        ],
        [
            {"host": "2001:ff:2::1"},
            {
                "host": "2001:ff:2::1",
                "port": 1312,
                "log": DEFAULT_LOG_CONF,
                "graphiql": False,
            },
        ],
        [
            {"port": 13121},
            {
                "host": "0.0.0.0",
                "port": 13121,
                "log": DEFAULT_LOG_CONF,
                "graphiql": False,
            },
        ],
        [
            {},
            {
                "host": "0.0.0.0",
                "port": 1312,
                "log": DEFAULT_LOG_CONF,
                "graphiql": False,
            },
        ],
    ],
)
def test_override_conf(
    conf_data: T.Dict[T.Text, T.Any],
    result: T.Dict[T.Text, T.Any],
    tmpdir: py.path.local,
) -> None:
    """Test the overrided conf."""
    conf_path = fill_mock_conf(conf_data, tmpdir)
    with mock.patch("kofi.config._find_conf", return_value=str(conf_path)):
        conf = read_config()

    assert conf == result


@pytest.mark.parametrize(
    "host", ["1234.5.6.7", "1.2.3.4.5", "1:2:3:4:5:6:7:8:9", "12345::1"]
)
def test_host_validation(host: T.Text, tmpdir: py.path.local) -> None:
    """Test the conf validation"""
    conf_path = fill_mock_conf({"host": host}, tmpdir)
    with pytest.raises(ValueError) as e:
        with mock.patch("kofi.config._find_conf", return_value=str(conf_path)):
            conf = read_config()

    assert "is invalid in configuration" in str(e.value)
    assert host in str(e.value)


@pytest.mark.parametrize("port", [-12, 66666])
def test_port_validation(port: int, tmpdir: py.path.local) -> None:
    """Test the conf validation"""
    conf_path = fill_mock_conf({"port": port}, tmpdir)
    with pytest.raises(ValueError) as e:
        with mock.patch("kofi.config._find_conf", return_value=str(conf_path)):
            conf = read_config()

    assert "is invalid in configuration" in str(e.value)
    assert str(port) in str(e.value)


@pytest.mark.parametrize(
    "log_conf, msg",
    [
        [{"level": "WARN"}, "Allowed values are ('DEBUG', 'INFO', 'WARNING', 'ERROR')"],
        [{"syslog": 1}, "Allowed values are ('true', 'false')"],
        [
            {"log_file": "/not/existing/path/to/logfile"},
            "Base directory does not exist",
        ],
    ],
)
def test_log_validation(
    log_conf: T.Dict[T.Text, T.Any], msg: T.Text, tmpdir: py.path.local
) -> None:
    """Test the conf validation"""
    conf_path = fill_mock_conf({"log": log_conf}, tmpdir)
    with pytest.raises(ValueError) as e:
        with mock.patch("kofi.config._find_conf", return_value=str(conf_path)):
            conf = read_config()

    assert "is invalid in configuration" in str(e.value)
    assert msg in str(e.value)
