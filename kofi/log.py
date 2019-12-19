# -*- encoding: utf-8 -*-
"""In this module are the tools to configure the logger."""

import logging
import logging.handlers
import sys
import typing as T


def setup_log(config: T.Dict[T.Text, T.Any]) -> logging.Logger:
    """Setup the logger."""
    fmt = setup_formatter()
    level = getattr(logging, config["level"])
    handlers = [setup_console_handler(fmt, level)]
    if config["syslog"]:
        handlers.append(setup_syslog_handler(fmt, level))
    path = config.get("log_file")
    if path:
        handlers.append(setup_file_handler(path, fmt, level))

    logger = logging.getLogger()
    logger.setLevel(level=level)
    for hdlr in handlers:
        logger.addHandler(hdlr)

    return logger


def setup_formatter() -> logging.Formatter:
    """Setting up a custom formatter."""
    return logging.Formatter(
        fmt="%(levelname)s -> [%(asctime)s][%(name)s|%(module)s] %(message)s"
    )


def setup_console_handler(fmt: logging.Formatter, level: int) -> logging.Handler:
    """Setup the handler that outputs on console."""
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(fmt)
    handler.setLevel(level)
    return handler


def setup_syslog_handler(fmt: logging.Formatter, level: int) -> logging.Handler:
    """Setup the syslog handler."""
    handler = logging.handlers.SysLogHandler()
    handler.setFormatter(fmt)
    handler.setLevel(level)
    return handler


def setup_file_handler(
    filename: T.Text, fmt: logging.Formatter, level: int
) -> logging.Handler:
    """Setup the file handler."""
    handler = logging.handlers.RotatingFileHandler(filename)
    handler.setFormatter(fmt)
    handler.setLevel(level)
    return handler
