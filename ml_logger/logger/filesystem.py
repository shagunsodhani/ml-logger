"""Functions to interface with the filesystem"""

import json
import logging

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType


def _serialize_log_to_json(log: LogType) -> str:
    """Serialize the log into a JSON string

    Args:
        log (LogType): Log to be serialized

    Returns:
        str: JSON serialized string
    """
    return json.dumps(log)


def _get_logger(logger_name: str = "default_logger") -> logging.Logger:
    """Get logger for a given name

    Args:
        logger_name (str, optional): Name of the logger (to retrieve).
            Defaults to "default_logger"

    Returns:
        logging.Logger: Logger object
    """
    return logging.getLogger(name=logger_name)


def _set_logger(
    logger_file_path: str, logger_name: str = "default_logger",
) -> logging.Logger:
    """Set logger to log to the given path

    Modified from https://docs.python.org/3/howto/logging-cookbook.html

    Args:
        logger_file_path (str): Filepath to write to
        logger_name (str, optional): Name of the logger to use. Defaults
            to "default_logger"

    Returns:
        logging.Logger: Logger object
    """
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(level=logging.INFO)
    # create file handler which logs all the messages
    file_handler = logging.FileHandler(filename=logger_file_path)
    file_handler.setLevel(level=logging.INFO)
    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(fmt="%(message)s")
    file_handler.setFormatter(fmt=formatter)
    stream_handler.setFormatter(fmt=formatter)
    # add the handlers to the logger
    logger.addHandler(hdlr=file_handler)
    logger.addHandler(hdlr=stream_handler)
    return logger


class Logger(BaseLogger):
    """Logger class that writes to the filesystem
    """

    def __init__(self, config: ConfigType):
        """Initialise the Filesystem Logger

        Args:
            config (ConfigType): config to initialise the filesystem logger.
                It must have two keys: logger_file_path and logger_name.
                "logger_file_path" is the path to the file where the logs
                will be written. "logger_name" is the name of the logger instance
        """
        super().__init__(config=config)
        assert "logger_file_path" in config
        assert "logger_name" in config

        self.logger = _set_logger(
            logger_file_path=config["logger_file_path"],
            logger_name=config["logger_name"],
        )

    def write_log(self, log: LogType) -> None:
        """Write the log to the filesystem

        Args:
            log (LogType): Log to write
        """

        log_str = _serialize_log_to_json(log=self._prepare_log_to_write(log))
        return self._write_log_to_fs(log_str=log_str)

    def _write_log_to_fs(self, log_str: str) -> None:
        """Write log string to filesystem

        Args:
            log_str (str): Log string to write
        """

        self.logger.info(msg=log_str)
