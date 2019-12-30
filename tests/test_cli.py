# -*- encoding: utf-8 -*-
"""Test the cli."""

from click.testing import CliRunner
import pytest

from kofi import cli

HELP_OUTPUT = """Usage: {name} [OPTIONS]

  Console script for kofi.

Options:
  -c, --config TEXT               The path to the config file.
  -b, --bind-address TEXT         The address to bind kofi to.
  -p, --port INTEGER              The port to bind kofi to.
  -l, --log-level [DEBUG|INFO|WARNING|ERROR]
                                  The log level
  --syslog                        Send the log also to the syslog
  --log-file PATH                 Send the log also to file
  --graphiql                      Enable the graphiql facility
  --help                          Show this message and exit.
"""


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


def test_command_line_interface(runner: CliRunner) -> None:
    """Test help."""
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert help_result.output == HELP_OUTPUT.format(name="main")


def test_host_validation(runner: CliRunner) -> None:
    """Test the validation for -b parameter."""
    invalid_res = runner.invoke(cli.main, ["-b", "1.2.3.4.5"])
    assert invalid_res.exit_code == 2
    assert 'Invalid value for "-b" / "--bind-address"' in invalid_res.output
    assert "'host' is invalid in configuration" in invalid_res.output


def test_port_validation(runner: CliRunner) -> None:
    """Test the validation for -p parameter."""
    invalid_res = runner.invoke(cli.main, ["-p", "66666"])
    assert invalid_res.exit_code == 2
    assert 'Invalid value for "-p" / "--port"' in invalid_res.output
    assert "'port' is invalid in configuration" in invalid_res.output
