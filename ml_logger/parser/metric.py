"""Implementation of Parser to parse the logs"""

import json
from typing import Callable, Dict, List, Optional

import pandas as pd

from ml_logger.parser import parser as base_parser
from ml_logger.parser import utils as parser_utils
from ml_logger.types import LogType, MetricType


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

        super().__init__(
            log_transformer=log_transformer, error_handler=error_handler,
        )
        self.log_type = "metric"

    def get_metrics_as_df(
        self,
        file_path: str,
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
        (iv) converts the merged metrics into dataframes and returns a list of dataframes

        Args:
            file_path (str): Log file to read from
            fn_to_group_metrics (Callable[[List[LogType]], Dict[str, List[LogType]]], optional):
                Function to group a list of metrics into a dictionary of
                (key, list of grouped metrics). Defaults to fn_to_group_metrics.
            fn_to_aggregate_metrics (Callable[[List[LogType]], List[LogType]], optional):
                Function to aggregate a list of metrics. Defaults to fn_to_aggregate_metrics.

        Returns:
            Dict[str, pd.DataFrame]: [description]

        """
        metric_logs = list(self.get_logs(file_path=file_path))
        return self.metrics_to_df(
            metric_logs=metric_logs,
            fn_to_group_metrics=fn_to_group_metrics,
            fn_to_aggregate_metrics=fn_to_aggregate_metrics,
        )

    def metrics_to_df(
        self,
        metric_logs: List[LogType],
        fn_to_group_metrics: Callable[
            [List[LogType]], Dict[str, List[LogType]]
        ] = fn_to_group_metrics,
        fn_to_aggregate_metrics: Callable[
            [List[LogType]], List[LogType]
        ] = fn_to_aggregate_metrics,
    ) -> Dict[str, pd.DataFrame]:
        """Create a dict of (metric_name, dataframe)

        Method that:
        (i) groups metrics
        (ii) merge all the metrics in a group,
        (iii) converts the merged metrics into dataframes and returns a list of dataframes

        Args:
            metric_logs (List[LogType]): List of metrics
            fn_to_group_metrics (Callable[[List[LogType]], Dict[str, List[LogType]]], optional):
                Function to group a list of metrics into a dictionary of
                (key, list of grouped metrics). Defaults to fn_to_group_metrics.
            fn_to_aggregate_metrics (Callable[[List[LogType]], List[LogType]], optional):
                Function to aggregate a list of metrics. Defaults to fn_to_aggregate_metrics.

        Returns:
            Dict[str, pd.DataFrame]: [description]

        """
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
