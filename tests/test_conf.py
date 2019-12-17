# -*- encoding: utf-8 -*-
"""Tests for the configuration parser"""

import os
import py  # type: ignore
import typing as T
from unittest import mock

import yaml
import pytest

from kofi.config import read_config, DEFAULT_LOG_CONF


def fill_mock_conf(conf: T.Dict[T.Text, T.Any], tmpdir: py.path.local) -> T.Text:
    base_dir = tmpdir.mkdir("conf")
    conf_path = base_dir.join("kofi.yml")
    with open(conf_path, "w") as f:
        f.write(yaml.dump(conf))

    return conf_path


@pytest.mark.parametrize(
    "conf_data, result",
    [
        [
            {
                "host": "127.0.0.1",
                "port": 13121,
                "log": {"level": "DEBUG", "syslog": True, "log_file": "/tmp/logfile",},
            },
            {
                "host": "127.0.0.1",
                "port": 13121,
                "log": {"level": "DEBUG", "syslog": True, "log_file": "/tmp/logfile",},
            },
        ],
        [
            {"host": "127.0.0.1", "log": {"syslog": True}},
            {
                "host": "127.0.0.1",
                "port": 1312,
                "log": {"level": "ERROR", "syslog": True},
            },
        ],
        [
            {"host": "2001:ff:2::1"},
            {"host": "2001:ff:2::1", "port": 1312, "log": DEFAULT_LOG_CONF},
        ],
        [{"port": 13121}, {"host": "0.0.0.0", "port": 13121, "log": DEFAULT_LOG_CONF}],
        [{}, {"host": "0.0.0.0", "port": 1312, "log": DEFAULT_LOG_CONF}],
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
