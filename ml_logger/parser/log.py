"""Implementation of Parser to parse the logs"""

import glob
from typing import Iterator, Optional

from ml_logger.parser.base import Parser as BaseParser
from ml_logger.parser.utils import parse_json
from ml_logger.types import LogType, ParseLineFunctionType


class Parser(BaseParser):
    """Class to parse the log files"""

    def __init__(self, parse_line: ParseLineFunctionType = parse_json):
        """Class to parse the log files

        Args:
            parse_line (ParseLineFunctionType):
                Function to parse a line in the log file. The function
                should return None if the line is not a valid log statement
                (eg error messages). Defaults to parse_json.
        """
        super().__init__(parse_line)
        self.log_type = "log"
        self.parse_line = self._wrap_parse_line(parse_line)

    def _wrap_parse_line(
        self, parse_line: ParseLineFunctionType
    ) -> ParseLineFunctionType:
        def fn(line: str) -> Optional[LogType]:
            log = parse_line(line)
            if log is not None and self.log_key not in log:
                log[self.log_key] = self.log_type
            return log

        return fn

    def _parse_file(self, file_path: str) -> Iterator[Optional[LogType]]:
        """Open a log file and parse its content

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

    def parse(self, filepath_pattern: str) -> Iterator[LogType]:
        """Open a log file, parse its contents and return `logs`

        Args:
            filepath_pattern (str): filepath pattern to glob

        Returns:
            Iterator[LogType]: Iterator over the logs

        Yields:
            Iterator[LogType]: Iterator over the logs
        """
        paths = glob.iglob(filepath_pattern)
        for file_path in paths:
            for log in self._parse_file(file_path):
                if log is not None:
                    yield log

    def parse_first_log(self, filepath_pattern: str) -> Optional[LogType]:
        """Return the first log from a file. The method will return after
        finding the first log. Unlike `parse()` method, it will not
        iterate over the entire log file (thus saving memory and time).

        Args:
            filepath_pattern (str): filepath pattern to glob

        Returns:
            LogType: First instance of a log

        """
        paths = glob.iglob(filepath_pattern)
        for file_path in paths:
            for log in self._parse_file(file_path):
                if log is not None:
                    return log
        return None

    def parse_last_log(self, filepath_pattern: str) -> Optional[LogType]:
        """Return the last log from a file. Like `parse()` method,
        it will iterate over the entire log file but will not keep all
        the logs in memory (thus saving memory).

        Args:
            filepath_pattern (str): filepath pattern to glob

        Returns:
            LogType: Last instance of a log

        """
        last_log: Optional[LogType] = None
        paths = glob.iglob(filepath_pattern)
        for file_path in paths:
            for log in self._parse_file(file_path=file_path):
                if log is not None:
                    last_log = log
        return last_log
