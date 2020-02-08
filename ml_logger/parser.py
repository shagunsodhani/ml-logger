import json
from typing import Callable, Dict, Iterator, List, Optional

import pandas as pd

from ml_logger.types import LogType, MetricType, ValueType


def filter_metric_log(log: LogType) -> bool:
    key = "type"
    if key in log and log[key] == "metric":
        return True
    return False


def error_handler_when_parsing_log_file(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    print(f"Could not parse: {log_line} because of error: {error}")
    return None


def silent_error_handler_when_parsing_log_file(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    return None


def transform_log(log: LogType) -> LogType:
    return log


def fn_to_group_metrics(metrics: List[MetricType]) -> Dict[str, List[LogType]]:
    return {"all": metrics}


def fn_to_merge_metrics(metrics: List[MetricType]) -> List[LogType]:
    return metrics


def map_list_of_dicts_to_dict_of_lists(
    list_of_dicts: List[Dict[str, ValueType]]
) -> Dict[str, List[Optional[ValueType]]]:
    if not list_of_dicts:
        return {}
    keys = list_of_dicts[0].keys()
    dict_of_lists = {}
    for key in keys:
        dict_of_lists[key] = [_dict.get(key, None) for _dict in list_of_dicts]
    return dict_of_lists


class Parser:
    """Class to parse the log files"""

    def __init__(
        self,
        fn_to_transform_log: Callable[[LogType], LogType] = transform_log,
        fn_to_handle_error_when_parsing_log_file: Callable[
            [str, json.decoder.JSONDecodeError], Optional[LogType]
        ] = error_handler_when_parsing_log_file,
    ):

        self.fn_to_transform_log = fn_to_transform_log
        self.fn_to_handle_error_when_parsing_log_file = (
            fn_to_handle_error_when_parsing_log_file
        )

    def parse_log_file(self, log_file_path: str) -> Iterator[LogType]:
        """Method to open a log file and return all the logs as dicts"""
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

    def get_metric_logs(self, log_file_path: str) -> Iterator[LogType]:
        """Method to open a log file and return logs containing metric information"""
        for log in self.parse_log_file(log_file_path=log_file_path):
            if filter_metric_log(log):
                yield self.fn_to_transform_log(log)

    def get_metrics_as_df(
        self,
        log_file_path: str,
        fn_to_group_metrics: Callable[
            [List[LogType]], Dict[str, List[LogType]]
        ] = fn_to_group_metrics,
        fn_to_merge_metrics: Callable[
            [List[LogType]], List[LogType]
        ] = fn_to_merge_metrics,
    ) -> Dict[str, pd.DataFrame]:
        """Method that:
        (i) reads the requested metrics (for each specified mode),
        (ii) groups metrics
        (iii) merge all the metrics in a group,
        (iii) converts the merged metrics into dataframes and returns a list of dataframes.
        """
        metric_logs = list(self.get_metric_logs(log_file_path=log_file_path))
        grouped_metrics: Dict[str, List[LogType]] = fn_to_group_metrics(metric_logs)
        merged_metrics = {
            key: fn_to_merge_metrics(metrics)
            for key, metrics in grouped_metrics.items()
        }

        metric_dfs = {
            key: pd.DataFrame.from_dict(
                data=map_list_of_dicts_to_dict_of_lists(metrics)
            )
            for key, metrics in merged_metrics.items()
        }
        return metric_dfs
