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
        self.log_transformer = log_transformer
        self.error_handler = error_handler
        self.log_type: Optional[str] = None


        """


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
