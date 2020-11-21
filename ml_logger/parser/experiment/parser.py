"""Implementation of Parser to parse experiment from the logs."""

import glob
from typing import Optional

from ml_logger.parser import base as base_parser
from ml_logger.parser.config import (
    parse_json_and_match_key as default_config_line_parser,
)
from ml_logger.parser.experiment.experiment import Experiment
from ml_logger.parser.metric import metrics_to_df
from ml_logger.parser.metric import (
    parse_json_and_match_key as default_metric_line_parser,
)
from ml_logger.parser.utils import parse_json
from ml_logger.types import LogType, ParseLineFunctionType


class Parser(base_parser.Parser):
    """Class to parse an experiment from the log dir."""

    def __init__(
        self,
        parse_config_line: ParseLineFunctionType = default_config_line_parser,
        parse_metric_line: ParseLineFunctionType = default_metric_line_parser,
        parse_info_line: ParseLineFunctionType = parse_json,
    ):
        """Class to parse experiment from the logs.

        Args:
            parse_config_line (ParseLineFunctionType):
                Function to parse a config line in the log file. The function
                should return None if the line is not a valid config log
                (eg error messages)
            parse_metric_line (ParseLineFunctionType):
                Function to parse a metric line in the log file. The function
                should return None if the line is not a valid metric log
                (eg error messages)
        """
        self.log_key = "logbook_type"
        self.log_type = "experiment"
        self.parse_line = self._wrap_parse_line(
            parser_functions={
                "config": parse_config_line,
                "metric": parse_metric_line,
                "info": parse_json,
            }
        )

    def parse(self, filepath_pattern: str) -> Experiment:
        """Load one experiment from the log dir.

        Args:
            filepath_pattern (str): filepath pattern to glob
        Returns:
            Experiment
        """
        configs = []
        metric_logs = []
        info: Dict[Any, Any] = {}
        paths = glob.glob(filepath_pattern)
        for file_path in paths:
            for log in self._parse_file(file_path=file_path):
                # At this point, if log is not None, it will have a key self.log_key
                if log is not None:
                    if log[self.log_key] == "config":
                        configs.append(log)
                    elif log[self.log_key] == "metric":
                        metric_logs.append(log)
                    else:
                        info_key = log[self.log_key]
                        if info_key not in info:
                            info[info_key] = []
                        info[info_key].append(log)
        return Experiment(
            configs=configs, metrics=metrics_to_df(metric_logs=metric_logs), info=info
        )
