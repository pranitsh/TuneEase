import pytest
import logging
from ..logger import ServerLogger


def test_ServerLogger_init():
    server_logger = ServerLogger("test.log")
    assert isinstance(server_logger, ServerLogger)
    assert isinstance(server_logger.logger, logging.Logger)


def test_ServerLogger_get():
    server_logger = ServerLogger("test.log")
    logger = server_logger.get()
    assert logger is server_logger.logger
    assert isinstance(logger, logging.Logger)
