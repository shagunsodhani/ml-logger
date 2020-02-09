"""Functions to interface with the filesystem

"""

import json
import logging
from typing import List, Optional, Tuple

from ml_logger import utils
from ml_logger.types import LogType


def _serialize_log_to_json(log: LogType) -> str:
    """Serialize the log into a JSON string

    Args:
        log (LogType): Log to be serialized

    Returns:
        str: JSON serialized string
    """
    return json.dumps(log)


def write_log(log_str: str, logger_name: str = "default_logger") -> None:
    """Write log string to file

    Args:
        log_str (str): Log string to write
        logger_name (str, optional):  Name of logger to use. Defaults
            to "default_logger"
    """

    return _get_logger(logger_name=logger_name).info(msg=log_str)


def _serialize_log(
    log: LogType,
    keys_to_serialize: Optional[List[str]] = None,
    log_type: str = "metric",
) -> Tuple[str, LogType]:
    """Serialize the log into a JSON string

    This method adds `type` field to the log and serializes only
    selected keys. If `keys_to_serialize` is not empty, only keys
    appearing in the `keys_to_serialize` are serialized

    Args:
        log (LogType): log to serialize
        keys_to_serialize (Optional[List[str]], optional): keys
            (in log) to serialize. If None is passed, all the keys are
            serialized. Defaults to None.
        log_type (str, optional): `type` of this log. Defaults to "metric"

    Returns:
        Tuple[str, LogType]: serialized log string and modified log object
    """
    log_to_serialize = {}
    if keys_to_serialize is not None:
        for key in keys_to_serialize:
            if key in log:
                log_to_serialize[key] = log[key]
    else:
        log_to_serialize = log
    log_to_serialize["type"] = log_type
    return _serialize_log_to_json(log=log_to_serialize), log


def write_message_log(
    message_log: LogType, logger_name: str = "default_logger"
) -> None:
    """Write message (log) to file

    Args:
        message_log (LogType): Message to write
        logger_name (str, optional):  Name of logger to use. Defaults
            to "default_logger"
    """
    log_str, _ = _serialize_log(
        log=message_log, keys_to_serialize=None, log_type="print"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def write_message(message: str, logger_name: str = "default_logger") -> None:
    """Write message (string) to file

    Args:
        message (str): Message to write
        logger_name (str, optional):  Name of logger to use. Defaults to
            "default_logger"
    """
    message_log: LogType = {"message": message}
    write_message_log(message_log=message_log, logger_name=logger_name)


def write_config_log(config: LogType, logger_name: str = "default_logger") -> None:
    """Write config to file

    Args:
        config (LogType): config to write
        logger_name (str, optional):  Name of logger to use. Defaults to
            "default_logger"
    """
    log_str, _ = _serialize_log(log=config, keys_to_serialize=None, log_type="config")
    write_log(log_str=log_str, logger_name=logger_name)


def write_metric_log(metric: LogType, logger_name: str = "default_logger") -> None:
    """Write metric to file

    Args:
        metric (LogType): metric to write
        logger_name (str, optional): Name of logger to use. Defaults to
            "default_logger"
    """
    log_str, _ = _serialize_log(
        log=utils.flatten_dict(metric), keys_to_serialize=None, log_type="metric"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def write_metadata_log(metadata: LogType, logger_name: str = "default_logger") -> None:
    """Write metadata to file

    Args:
        metadata (LogType): metadata to write
        logger_name (str, optional): Name of logger to use. Defaults to
            "default_logger"
    """
    log_str, _ = _serialize_log(
        log=metadata, keys_to_serialize=None, log_type="metadata"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def pprint(log: LogType) -> None:
    """Pretty print a log

    Args:
        log (LogType): log to print
    """
    print(json.dumps(log, indent=4))


def set_logger(
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


def _get_logger(logger_name: str = "default_logger") -> logging.Logger:
    """Get logger for a given name

    Args:
        logger_name (str, optional): Name of the logger (to retrieve).
            Defaults to "default_logger"

    Returns:
        logging.Logger: Logger object
    """
    return logging.getLogger(name=logger_name)
