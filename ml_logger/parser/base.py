"""Base class that all parsers extend."""

from abc import ABC
from pathlib import Path
from typing import Dict, Iterator, Optional, Union

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

    def _parse_file(self, file_path: Union[str, Path]) -> Iterator[Optional[LogType]]:
        """Open a log file and parse its content.

        Args:
            file_path (Union[str, Path]): Log file to read from

        Returns:
            Iterator[Optional[LogType]]: Iterator over the logs

        Yields:
            Iterator[Optional[LogType]]: Iterator over the logs
        """
        with open(file_path) as f:
            for line in f:
                log = self.parse_line(line)
                yield log

    def _wrap_parse_line(
        self, parser_functions: Dict[str, ParseLineFunctionType]
    ) -> ParseLineFunctionType:
        def fn(line: str) -> Optional[LogType]:
            log = None
            for parser_type, parser_func in parser_functions.items():
                log = parser_func(line)
                if log is not None:
                    if not isinstance(log, dict):
                        log = {"data": log}
                    if self.log_key not in log:
                        log[self.log_key] = parser_type
                    break
            return log

        return fn
