"""Implementation of Parser to parse the logs"""

import json
from typing import Callable, Iterator, Optional

from ml_logger.parser import parser as base_parser
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
        fn_to_transform_log: Callable[[LogType], LogType] = base_parser.transform_log,
        fn_to_handle_error_when_parsing_log_file: Callable[
            [str, json.decoder.JSONDecodeError], Optional[LogType]
        ] = base_parser.error_handler_when_parsing_log_file,
    ):
        """Class to parse the log files

        Args:
            fn_to_transform_log (Callable[[LogType], LogType], optional):
                Function to transform the logs after reading them from
                the filesystem. Defaults to transform_log.
            fn_to_handle_error_when_parsing_log_file (Callable[[str,
                json.decoder.JSONDecodeError], Optional[LogType]], optional):
                Function to handle the error when the parser reads an
                invalid json string

        """

        super().__init__(
            fn_to_transform_log=fn_to_transform_log,
            fn_to_handle_error_when_parsing_log_file=fn_to_handle_error_when_parsing_log_file,
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

    def get_config(self, log_file_path: str) -> ConfigType:
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
        return configs[-1]
