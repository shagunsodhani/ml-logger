"""Functions to interface with the filesystem"""

import json
import logging
import os

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
    logger_file_path: str,
    logger_name: str = "default_logger",
    write_to_console: bool = True,
) -> logging.Logger:
    """Set logger to log to the given path

    Modified from https://docs.python.org/3/howto/logging-cookbook.html

    Args:
        logger_file_path (str): Filepath to write to
        logger_name (str, optional): Name of the logger to use. Defaults
            to "default_logger"
        write_to_console (bool, optional): Should write the logs to console.
            Defaults to True

    Returns:
        logging.Logger: Logger object
    """
    logger = logging.getLogger(name=logger_name)
    logger.setLevel(level=logging.INFO)
    # create file handler which logs all the messages
    file_handler = logging.FileHandler(filename=logger_file_path)
    file_handler.setLevel(level=logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(fmt="%(message)s")
    file_handler.setFormatter(fmt=formatter)
    # add the handlers to the logger
    logger.addHandler(hdlr=file_handler)

    if write_to_console:
        # create console handler with a higher log level
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=logging.INFO)
        # add formatter to the handlers
        stream_handler.setFormatter(fmt=formatter)
        # add the handlers to the logger
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
        assert "logger_dir" in config
        assert "logger_name" in config
        assert "write_to_console" in config
        assert "create_multiple_log_files" in config

        logger_types = ["config", "message", "metadata", "metric"]

        if config["create_multiple_log_files"]:

            self.loggers = {
                _type: _set_logger(
                    logger_file_path=os.path.join(
                        config["logger_dir"], f"{_type}.jsonl"
                    ),
                    logger_name=config["logger_name"] + "_" + _type,
                    write_to_console=config["write_to_console"],
                )
                for _type in logger_types
            }

        else:
            logger = _set_logger(
                logger_file_path=os.path.join(config["logger_dir"], "log.jsonl"),
                logger_name=config["logger_name"],
                write_to_console=config["write_to_console"],
            )
            self.loggers = {_type: logger for _type in logger_types}

    def write_log(self, log: LogType) -> None:
        """Write the log to the filesystem

        Args:
            log (LogType): Log to write
        """

        log_str = _serialize_log_to_json(log=self._prepare_log_to_write(log))
        return self._write_log_to_fs(log_str=log_str, log_type=log["logbook_type"])

    def _write_log_to_fs(self, log_str: str, log_type: str) -> None:
        """Write log string to filesystem

        Args:
            log_str (str): Log string to write
            log_type (str): Type of log to write
        """
        self.loggers[log_type].info(msg=log_str)
