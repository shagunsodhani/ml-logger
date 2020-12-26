"""Implementation of Parser to parse experiment from the logs."""

import glob
import os
from pathlib import Path
from typing import Any, Dict, Union

from ml_logger.parser import base as base_parser
from ml_logger.parser.config import (
    parse_json_and_match_value as default_config_line_parser,
)
from ml_logger.parser.experiment.experiment import Experiment
from ml_logger.parser.metric import metrics_to_df
from ml_logger.parser.metric import (
    parse_json_and_match_value as default_metric_line_parser,
)
from ml_logger.parser.utils import parse_json
from ml_logger.types import ParseLineFunctionType


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
                "info": parse_info_line,
            }
        )

    def parse(self, filepath_pattern: Union[str, Path]) -> Experiment:
        """Load one experiment from the log dir.

        Args:
            filepath_pattern (Union[str, Path]): filepath pattern to glob
                or instance of Path (directory) object.
        Returns:
            Experiment
        """
        configs = []
        metric_logs = []
        info: Dict[Any, Any] = {}
        # check if filepath_pattern is a directory
        if os.path.isdir(filepath_pattern):
            filepath_pattern = Path(filepath_pattern)
            # convert the filepath_patter to a Path object.
        if isinstance(filepath_pattern, Path):
            if filepath_pattern.is_dir():
                # iterate over all the files in the directory.
                paths = list(filepath_pattern.iterdir())
            else:
                paths = [filepath_pattern]
        else:
            paths = [Path(_path) for _path in glob.glob(filepath_pattern)]
        paths = [_path for _path in paths if _path.is_file()]
        assert paths, "No logs to parse"
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
