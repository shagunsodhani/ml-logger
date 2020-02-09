"""Implementation of Parser to parse the logs"""

import json
from typing import Callable, Dict, Iterator, List, Optional

import pandas as pd

from ml_logger.types import LogType, MetricType, ValueType


def filter_metric_log(log: LogType) -> bool:
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


def error_handler_when_parsing_log_file(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    """Function to print the error on the console, when the `log_line` is
        not a valid json string

    Args:
        log_line (str): Parsing this line triggered the error
        error (json.decoder.JSONDecodeError): The error object

    Returns:
        Optional[LogType]: None. Print the error on the console
    """
    print(f"Could not parse: {log_line} because of error: {error}")
    return None


def silent_error_handler_when_parsing_log_file(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    """Function to silently ignore the error, when the `log_line` is
        not a valid json string

    Args:
        log_line (str): Parsing this line triggered the error
        error (json.decoder.JSONDecodeError): The error object

    Returns:
        Optional[LogType]: None. Nothing is done
    """
    return None


def transform_log(log: LogType) -> LogType:
    """Function to transform the log after parsing

    Args:
        log (LogType): log to transform

    Returns:
        LogType: transformed log
    """
    return log


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


def map_list_of_dicts_to_dict_of_lists(
    list_of_dicts: List[Dict[str, ValueType]]
) -> Dict[str, List[Optional[ValueType]]]:
    """Map a list of dictionary to a dictionary of lists

    Example input: [
        {"a": 1, "b": 2},
        {"b": 3, "c": 4},
    ]

    Example output: {
        "a": [1],
        "b": [2, 3],
        "c": [4]
    }

    Args:
        list_of_dicts (List[Dict[str, ValueType]]): List of dictionaries

    Returns:
        Dict[str, List[Optional[ValueType]]]: Dictionary of lists
    """
    if not list_of_dicts:
        return {}
    keys = list_of_dicts[0].keys()
    dict_of_lists = {}
    for key in keys:
        dict_of_lists[key] = [_dict.get(key, None) for _dict in list_of_dicts]
    return dict_of_lists


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

                [description]. Defaults to error_handler_when_parsing_log_file.
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

    def get_metric_logs(self, log_file_path: str) -> Iterator[MetricType]:
        """Method to open a log file, parse the logs and return metric logs

        Args:
            log_file_path (str): Log file to read from

        Returns:
            Iterator[MetricType]: Iterator over the metrics

        Yields:
            Iterator[MetricType]: Iterator over the metrics
        """
        for log in self.parse_log_file(log_file_path=log_file_path):
            if filter_metric_log(log):
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
        metric_logs = list(self.get_metric_logs(log_file_path=log_file_path))
        grouped_metrics: Dict[str, List[LogType]] = fn_to_group_metrics(metric_logs)
        merged_metrics = {
            key: fn_to_aggregate_metrics(metrics)
            for key, metrics in grouped_metrics.items()
        }

        metric_dfs = {
            key: pd.DataFrame.from_dict(
                data=map_list_of_dicts_to_dict_of_lists(metrics)
            )
            for key, metrics in merged_metrics.items()
        }
        return metric_dfs
