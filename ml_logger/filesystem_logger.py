"""Logging functions to interface with the filesystem"""
import json
import logging
from typing import List, MutableMapping, Tuple

from ml_logger import utils
from ml_logger.types import LogType, ValueType


def serialize_log(log: LogType) -> str:
    """Serialize the log before converting into the json string"""
    return json.dumps(log)


def write_log(log_str: str, logger_name: str = "default_logger") -> None:
    """This is the default method to write a log.
    It is assumed that the log has already been processed
     before feeding to this method"""
    get_logger(logger_name=logger_name).info(msg=log_str)


def serialize_custom_log(
    keys_to_serialize: List[str], log: LogType, log_type: str = "metric"
) -> Tuple[str, LogType]:
    """Method to serialize the custom logs.
    If keys_to_serialize is not empty, only keys appearing in the keys_to_serialize are serialized."""
    log_to_serialize = {}
    if keys_to_serialize:
        for key in keys_to_serialize:
            if key in log:
                log_to_serialize[key] = log[key]
    else:
        log_to_serialize = log
    log_to_serialize["type"] = log_type
    return serialize_log(log=log_to_serialize), log


def write_message_log(
    message_log: LogType, logger_name: str = "default_logger"
) -> None:
    """"Write message logs"""
    log_str, _ = serialize_custom_log(
        keys_to_serialize=[], log=message_log, log_type="print"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def write_message(message: str, logger_name: str = "default_logger") -> None:
    """"Write message"""
    message_log: LogType = {"message": message}
    write_message_log(message_log=message_log, logger_name=logger_name)


def write_config_log(config: LogType, logger_name: str = "default_logger") -> None:
    """Write config logs"""
    log_str, _ = serialize_custom_log(
        keys_to_serialize=[], log=config, log_type="config"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def write_metric_log(metric: LogType, logger_name: str = "default_logger") -> None:
    """Write metric logs"""
    log_str, _ = serialize_custom_log(
        keys_to_serialize=[], log=utils.flatten_dict(metric), log_type="metric"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def write_metadata_log(metadata: LogType, logger_name: str = "default_logger") -> None:
    """Write metadata logs"""
    log_str, _ = serialize_custom_log(
        keys_to_serialize=[], log=metadata, log_type="metadata"
    )
    write_log(log_str=log_str, logger_name=logger_name)


def pprint(config: LogType) -> None:
    """pretty print a json dict"""
    print(json.dumps(config, indent=4))


def set_logger(
    logger_file_path: str, logger_name: str = "default_logger",
) -> logging.Logger:
    """Modified from
    https://docs.python.org/3/howto/logging-cookbook.html"""
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


def get_logger(logger_name: str = "default_logger") -> logging.Logger:
    """get logger"""
    return logging.getLogger(name=logger_name)
