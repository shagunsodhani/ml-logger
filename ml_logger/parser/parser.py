"""Implementation of Parser to parse the logs"""

import json
from typing import Callable, Iterator, Optional

from ml_logger.parser import utils as parser_utils
from ml_logger.types import LogType


class Parser:
    """Class to parse the log files
    """

    def __init__(
        self,
        fn_to_transform_log: Callable[[LogType], LogType] = transform_log,
        fn_to_handle_error_when_parsing_log_file: Callable[
            [str, json.decoder.JSONDecodeError], Optional[LogType]
        ] = error_handler_when_parsing_log_file,
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

        self.fn_to_transform_log = fn_to_transform_log
        self.fn_to_handle_error_when_parsing_log_file = (
            fn_to_handle_error_when_parsing_log_file
        )

    def parse_log_file(self, log_file_path: str) -> Iterator[LogType]:
        """Method to open a log file and parse the logs

        Args:
            log_file_path (str): Log file to read from

        Returns:
            Iterator[LogType]: Iterator over the logs

        Yields:
            Iterator[LogType]: Iterator over the logs
        """
        with open(log_file_path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.decoder.JSONDecodeError as e:
                    # This could be the scase where a new line was missing
                    error_handler_response = self.fn_to_handle_error_when_parsing_log_file(
                        line, e
                    )
                    if error_handler_response is not None:
                        yield error_handler_response

    def get_logs(self, log_file_path: str) -> Iterator[LogType]:
        """Method to open a log file, parse the logs and return logs

        Args:
            log_file_path (str): Log file to read from

        Returns:
            Iterator[LogType]: Iterator over the logs

        Yields:
            Iterator[LogType]: Iterator over the logs
        """
        for log in self.parse_log_file(log_file_path=log_file_path):
            if filter_log(log):
                yield self.fn_to_transform_log(log)
