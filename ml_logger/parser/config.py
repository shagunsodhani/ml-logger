"""Implementation of Parser to parse config from logs."""

from typing import Optional

from ml_logger.parser import log as log_parser
from ml_logger.parser.utils import parse_json
from ml_logger.types import LogType, ParseLineFunctionType


def parse_json_and_match_key(line: str) -> Optional[LogType]:
    """Parse a line as JSON string and check if it a valid log."""
    log = parse_json(line)
    if log:
        key = "logbook_type"
        if key not in log or log[key] != "config":
            log = None
    return log


class Parser(log_parser.Parser):
    """Class to parse config from the logs."""

    def __init__(self, parse_line: ParseLineFunctionType = parse_json_and_match_key):
        """Class to parse config from the log.

        Args:
            parse_line (ParseLineFunctionType):
                Function to parse a line in the log file. The function
                 should return None if the line is not a valid config (eg
                 error messages). Defaults to parse_json_and_match_key.
        """
        super().__init__(parse_line=parse_line)
        self.log_type = "config"
