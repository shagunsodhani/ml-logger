"""Implementation of Parser to parse metrics from logs."""

from typing import Callable, Dict, List, Optional

import pandas as pd

from ml_logger.parser import log as log_parser
from ml_logger.parser.utils import parse_json
from ml_logger.types import LogType, MetricType, ParseLineFunctionType


def parse_json_and_match_key(line: str) -> Optional[LogType]:
    """Parse a line as JSON string and check if it a valid metric log."""
    log = parse_json(line)
    if log:
        key = "logbook_type"
        if key not in log or log[key] != "metric":
            log = None
    return log


def group_metrics(metrics: List[MetricType]) -> Dict[str, List[MetricType]]:
    """Group a list of metrics.

    Group a list of metrics into a dictionary of
        (key, list of grouped metrics)

    Args:
        metrics (List[MetricType]): List of metrics to group

    Returns:
        Dict[str, List[MetricType]]: Dictionary of (key,
            list of grouped metrics)
    """
    return {"all": metrics}


def aggregate_metrics(metrics: List[MetricType]) -> List[MetricType]:
    """Aggregate a list of metrics.

    Args:
        metrics (List[MetricType]): List of metrics to aggregate

    Returns:
        List[MetricType]: List of aggregated metrics
    """
    return metrics


class Parser(log_parser.Parser):
    """Class to parse the metrics from the logs."""

    def __init__(self, parse_line: ParseLineFunctionType = parse_json_and_match_key):
        """Class to parse the metrics from the logs.

        Args:
            parse_line (ParseLineFunctionType):
                Function to parse a line in the log file. The function
                should return None if the line is not a valid log statement
                (eg error messages). Defaults to parse_json_and_match_key.
        """
        super().__init__(parse_line)
        self.log_type = "metric"

    def parse_as_df(
        self,
        filepath_pattern: str,
        group_metrics: Callable[
            [List[LogType]], Dict[str, List[LogType]]
        ] = group_metrics,
        aggregate_metrics: Callable[[List[LogType]], List[LogType]] = aggregate_metrics,
    ) -> Dict[str, pd.DataFrame]:
        """Create a dict of (metric_name, dataframe).

        Method that:
        (i) reads metrics from the filesystem
        (ii) groups metrics
        (iii) aggregates all the metrics within a group,
        (iv) converts the aggregate metrics into dataframes and returns a \
            dictionary of dataframes

        Args:
            filepath_pattern (str): filepath pattern to glob
            group_metrics (Callable[[List[LogType]], Dict[str, List[LogType]]], optional):
                Function to group a list of metrics into a dictionary of
                (key, list of grouped metrics). Defaults to group_metrics.
            aggregate_metrics (Callable[[List[LogType]], List[LogType]], optional):
                Function to aggregate a list of metrics. Defaults to aggregate_metrics.

        """
        metric_logs = list(self.parse(filepath_pattern))
        return metrics_to_df(
            metric_logs=metric_logs,
            group_metrics=group_metrics,
            aggregate_metrics=aggregate_metrics,
        )


def metrics_to_df(
    metric_logs: List[LogType],
    group_metrics: Callable[[List[LogType]], Dict[str, List[LogType]]] = group_metrics,
    aggregate_metrics: Callable[[List[LogType]], List[LogType]] = aggregate_metrics,
) -> Dict[str, pd.DataFrame]:
    """Create a dict of (metric_name, dataframe).

    Method that:
    (i) groups metrics
    (ii) aggregates all the metrics within a group,
    (iii) converts the aggregate metrics into dataframes and returns a \
        dictionary of dataframes

    Args:
        metric_logs (List[LogType]): List of metrics
        group_metrics (Callable[[List[LogType]], Dict[str, List[LogType]]], optional):
            Function to group a list of metrics into a dictionary of
            (key, list of grouped metrics). Defaults to group_metrics.
        aggregate_metrics (Callable[[List[LogType]], List[LogType]], optional):
            Function to aggregate a list of metrics. Defaults to aggregate_metrics.

    Returns:
        Dict[str, pd.DataFrame]: [description]

    """
    grouped_metrics: Dict[str, List[LogType]] = group_metrics(metric_logs)
    aggregated_metrics = {
        key: aggregate_metrics(metrics) for key, metrics in grouped_metrics.items()
    }

    metric_dfs = {
        key: pd.json_normalize(data=metrics)
        for key, metrics in aggregated_metrics.items()
    }
    return metric_dfs
