"""Logging functions to interface with the filesystem"""
import json
import logging
from typing import Dict, List, Tuple

import multiprocessing_logging

from ml_logger.utils import flatten_dict


def format_log(log: Dict) -> str:
    """format the log dict before converting into the json string"""
    return json.dumps(log)


def write_log(log: Dict, logger_name: str = "default_logger") -> None:
    """This is the default method to write a log.
    It is assumed that the log has already been processed
     before feeding to this method"""
    get_logger(logger_name).info(log)


def read_log_string(log_string: str) -> Dict:
    """This is the single point to read any log message from the file.
     All the log messages are persisted as json strings in the filesystem"""
    try:
        data = json.loads(log_string)
    except json.JSONDecodeError as _:
        data = {}
    if data["type"] == "print":
        data = {}
    return data


def format_custom_logs(
    keys: List[str], raw_log: Dict, log_type: str = "metric"
) -> Tuple[str, Dict]:
    """Method to format the custom logs.
    If keys is not empty, only entries appearing in the keys are kept."""
    log = {}
    if keys:
        for key in keys:
            if key in raw_log:
                log[key] = raw_log[key]
    else:
        log = raw_log
    log["type"] = log_type
    return format_log(log), log


def write_message_logs(message: Dict, logger_name: str = "default_logger") -> None:
    """"Write message logs"""
    log, _ = format_custom_logs(keys=[], raw_log=message, log_type="print")
    write_log(log, logger_name=logger_name)


def write_message(message: str, logger_name: str = "default_logger") -> None:
    """"Write message"""
    message = {"message": message}
    log, _ = format_custom_logs(keys=[], raw_log=message, log_type="print")
    write_log(log, logger_name=logger_name)


def write_config_log(config: Dict, logger_name: str = "default_logger") -> None:
    """Write config logs"""
    log, _ = format_custom_logs(keys=[], raw_log=config, log_type="config")
    write_log(log, logger_name=logger_name)


def write_metric_logs(metric: Dict, logger_name: str = "default_logger") -> None:
    """Write metric logs"""
    keys = []
    log, _ = format_custom_logs(
        keys=keys, raw_log=flatten_dict(metric), log_type="metric"
    )
    write_log(log, logger_name=logger_name)


def write_metadata_logs(metadata: Dict, logger_name: str = "default_logger") -> None:
    """Write metadata logs"""
    log, _ = format_custom_logs(keys=[], raw_log=metadata, log_type="metadata")
    write_log(log, logger_name=logger_name)


def pprint(config: Dict) -> None:
    """pretty print a json dict"""
    print(json.dumps(config, indent=4))


def set_logger(
    logger_file_path: str,
    logger_name: str = "default_logger",
    use_multiprocessing_logging: bool = False,
) -> logging.RootLogger:
    """Modified from
    https://docs.python.org/3/howto/logging-cookbook.html"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    if use_multiprocessing_logging:
        multiprocessing_logging.install_mp_handler()
    # create file handler which logs all the messages
    file_handler = logging.FileHandler(logger_file_path)
    file_handler.setLevel(logging.INFO)
    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def get_logger(logger_name: str = "default_logger") -> logging.RootLogger:
    """get logger"""
    return logging.getLogger(logger_name)
