"""Implementation of Parser to parse the logs"""

import glob
import json
from typing import Callable, Optional

import tinydb

from ml_logger.parser import parser as base_parser
from ml_logger.parser import utils as parser_utils
from ml_logger.types import ConfigType, LogType


def filter_log(log: LogType) -> bool:
    """Check if the log is a config log

    Args:
        log (LogType): log to check

    Returns:
        bool: True if the log is a config log
    """
    key = "type"
    if key in log and log[key] == "config":
        return True
    return False


class Parser(base_parser.Parser):
    """Class to parse the config in the log files
    """

    def __init__(
        self,
        log_transformer: Callable[
            [LogType], LogType
        ] = parser_utils.identity_log_transformer,
        error_handler: Callable[
            [str, json.decoder.JSONDecodeError], Optional[LogType]
        ] = parser_utils.silent_error_handler,
    ):
        """Class to parse the log files

        Args:
            log_transformer (Callable[[LogType], LogType], optional):
                Function to transform the logs after reading them from the
                filesystem. Defaults to parser_utils.identity_log_transformer.
            error_handler (Callable[[str, json.decoder.JSONDecodeError],
                Optional[LogType]], optional): Function to handle the
                error when the parser reads an invalid json string.
                Defaults to parser_utils.silent_error_handler.
        """

        super().__init__(
            log_transformer=log_transformer, error_handler=error_handler,
        )

    def get_logs(self, log_file_path: str) -> Iterator[ConfigType]:
        """Method to open a log file, parse the logs and return config logs

        Args:
            log_file_path (str): Log file to read from

        Returns:
            Iterator[ConfigType]: Iterator over the configs

        Yields:
            Iterator[ConfigType]: Iterator over the configs
        """
        for log in self.parse_log_file(log_file_path=log_file_path):
            if filter_log(log):
                yield self.fn_to_transform_log(log)

    def get_config(self, log_file_path: str) -> Optional[ConfigType]:
        """Method to get the config from the log file.

        The different between `get_config` and `get_logs` function is that
        `get_logs` returns an iterator over all the configs that are found
        in a log file while `get_config` only returns the last config. The same
        config file may be written multiple times in a log file. Hence
        `get_config` should be the default method for getting the config

        Args:
            log_file_path (str): Log file to read from

        Returns:
            ConfigType: Config object
        """

        configs = list(self.get_logs(log_file_path=log_file_path))
        if configs:
            return configs[-1]
        return None

    def load_configs_from_path(self, path_pattern: str) -> tinydb.TinyDB:
        """Method to glob the given path pattern and load config from
        all the matching paths

        Args:
            path_pattern (str): path pattern to glob

        Returns:
            tinydb.TinyDB: TinyDB database instance over the collection of configs
        """
        db = tinydb.TinyDB("config.json")
        paths = glob.glob(path_pattern)
        for log_file_path in paths:
            config = self.get_config(log_file_path=log_file_path)
            if config is not None:
                config["path"] = log_file_path
                db.insert(config)
        return db
