"""Base class that all parsers extend."""

from abc import ABC
from typing import Iterator, Optional

from ml_logger.parser.utils import parse_json
from ml_logger.types import LogType, ParseLineFunctionType


class Parser(ABC):
    """Base class that all parsers extend."""

    def __init__(self, parse_line: ParseLineFunctionType = parse_json):
        """Class to parse the log files.

        Args:
            parse_line (ParseLineFunctionType):
                Function to parse a line in the log file. The function
                should return None if the line is not a valid log statement
                (eg error messages). Defaults to parse_json.
        """
        self.log_key = "logbook_type"
        self.log_type = "base_parser"
        self.parse_line = parse_line

    def _parse_file(self, file_path: str) -> Iterator[Optional[LogType]]:
        """Open a log file and parse its content.

        Args:
            file_path (str): Log file to read from

        Returns:
            Iterator[Optional[LogType]]: Iterator over the logs

        Yields:
            Iterator[Optional[LogType]]: Iterator over the logs
        """
        with open(file_path) as f:
            for line in f:
                log = self.parse_line(line)
                yield log
