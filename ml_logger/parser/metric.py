"""Implementation of Parser to parse the logs"""

import json
from typing import Callable, Dict, Iterator, List, Optional

import pandas as pd

from ml_logger.parser import parser as base_parser
from ml_logger.parser import utils as parser_utils
from ml_logger.types import LogType, MetricType


def filter_log(log: LogType) -> bool:
    """Check if the log is a metric log

    Args:
        log (LogType): log to check

    Returns:
        bool: True if the log is a metric log
    """
    key = "type"
    if key in log and log[key] == "metric":
        return True
    return False


def fn_to_group_metrics(metrics: List[MetricType]) -> Dict[str, List[MetricType]]:
    """Function to group a list of metrics into a dictionary of (key,
    list of grouped metrics)

    Args:
        metrics (List[MetricType]): List of metrics to group

    Returns:
        Dict[str, List[MetricType]]: Dictionary of (key,
            list of grouped metrics)
    """
    return {"all": metrics}


def fn_to_aggregate_metrics(metrics: List[MetricType]) -> List[MetricType]:
    """Function to aggregate a list of metrics

    Args:
        metrics (List[MetricType]): List of metrics to aggregate

    Returns:
        List[MetricType]: List of aggregated metrics
    """
    return metrics


class Parser(base_parser.Parser):
    """Class to parse the metrics in the log files
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

    def get_logs(self, log_file_path: str) -> Iterator[MetricType]:
        """Method to open a log file, parse the logs and return metric logs

        Args:
            log_file_path (str): Log file to read from

        Returns:
            Iterator[MetricType]: Iterator over the metrics

        Yields:
            Iterator[MetricType]: Iterator over the metrics
        """
        for log in self.parse_log_file(log_file_path=log_file_path):
            if filter_log(log):
                yield self.fn_to_transform_log(log)

    def get_metrics_as_df(
        self,
        log_file_path: str,
        fn_to_group_metrics: Callable[
            [List[LogType]], Dict[str, List[LogType]]
        ] = fn_to_group_metrics,
        fn_to_aggregate_metrics: Callable[
            [List[LogType]], List[LogType]
        ] = fn_to_aggregate_metrics,
    ) -> Dict[str, pd.DataFrame]:
        """Create a dict of (metric_name, dataframe)

        Method that:
        (i) reads the requested metrics (for each specified mode),
        (ii) groups metrics
        (iii) merge all the metrics in a group,
        (iii) converts the merged metrics into dataframes and returns a list of dataframes

        Args:
            log_file_path (str): Log file to read from
            fn_to_group_metrics (Callable[[List[LogType]], Dict[str, List[LogType]]], optional):
                Function to group a list of metrics into a dictionary of
                (key, list of grouped metrics). Defaults to fn_to_group_metrics.
            fn_to_aggregate_metrics (Callable[[List[LogType]], List[LogType]], optional):
                Function to aggregate a list of metrics. Defaults to fn_to_aggregate_metrics.

        Returns:
            Dict[str, pd.DataFrame]: [description]

        """
        metric_logs = list(self.get_logs(log_file_path=log_file_path))
        grouped_metrics: Dict[str, List[LogType]] = fn_to_group_metrics(metric_logs)
        merged_metrics = {
            key: fn_to_aggregate_metrics(metrics)
            for key, metrics in grouped_metrics.items()
        }

        metric_dfs = {
            key: pd.DataFrame.from_dict(
                data=parser_utils.map_list_of_dicts_to_dict_of_lists(metrics)
            )
            for key, metrics in merged_metrics.items()
        }
        return metric_dfs
