"""Implementation of Parser to parse the logs"""

import json
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union, overload

import pandas as pd

from ml_logger.logger import filesystem
from ml_logger.parser import parser as base_parser
from ml_logger.parser import utils as parser_utils
from ml_logger.parser.config import Parser as ConfigParser
from ml_logger.parser.metric import Parser as MetricParser
from ml_logger.types import LogType


class Experiment:
    def __init__(
        self, config: LogType, metrics: Dict[str, pd.DataFrame], logger_dir: str,
    ):
        self.config = config
        self.metrics = metrics
        self.logger_dir = logger_dir


class ExperimentSequence(Sequence):  # type: ignore
    """Provides a list-like interface to a collection of Experimente
    """

    def __init__(self, experiments: List[Experiment]):
        self.experiments = experiments
        super().__init__()

    def groupby(
        self, group_fn: Callable[[Experiment], str]
    ) -> Dict[str, "ExperimentSequence"]:
        """Group experiments in the sequence

        Args:
            group_fn: Function to assign a string group id to the experiment

        Returns:
            Dict[str, ExperimentSequence]: A dictionary mapping the sring
            group id to a sequence of experiments
        """
        grouped_experiments: Dict[str, List[Experiment]] = {}
        for experiment in self.experiments:
            key = group_fn(experiment)
            if key not in grouped_experiments:
                grouped_experiments[key] = []
            grouped_experiments[key].append(experiment)

        return {
            key: ExperimentSequence(value) for key, value in grouped_experiments.items()
        }

    def filter(self, filter_fn: Callable[[Experiment], bool]) -> "ExperimentSequence":
        """Filter experiments in the sequence

        Args:
            filter_fn: Function to filter an experiment

        Returns:
            ExperimentSequence: A sequence of experiments for which the
            filter condition is true
        """
        return ExperimentSequence(
            [experiment for experiment in self.experiments if filter_fn(experiment)]
        )

    @overload  # noqa:F811
    def __getitem__(self, index: int) -> Experiment:
        pass

    @overload  # noqa:F811
    def __getitem__(self, index: slice) -> "ExperimentSequence":
        pass

    def __getitem__(  # noqa:F811
        self, index: Union[int, slice]
    ) -> Union[Experiment, "ExperimentSequence"]:
        if isinstance(index, slice):
            return ExperimentSequence(self.experiments[index])
        else:
            return self.experiments[index]

    def __len__(self) -> int:
        return len(self.experiments)


class Parser(base_parser.Parser):
    """Class to parse the entire experiment from the log dir
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
        """Class to parse the experiment from the log files

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
        self.config_parser = ConfigParser(
            log_transformer=log_transformer, error_handler=error_handler
        )

        self.metric_parser = MetricParser(
            log_transformer=log_transformer, error_handler=error_handler
        )
        self.log_type = None

    def get_one_experiment(
        self, logger_dir: str, filename: Optional[str] = None, filename_prefix: str = ""
    ) -> Experiment:
        """Load one experiment from the log dir

        Args:
            logger_dir (str): Path where the logs will be read from.
            filename (Optional[str], optional): Name to assigned to the
            log file (eg log.jsonl). If None is passed, this argument is
            ignored and it is assumed that multiple log files are written
            per experiment (for config, metadata, metric etc).  If the
            value is set, `filename_prefix` argument is ignored. Defaults
            to None.
            filename_prefix (str, optional): String to prefix before the
            name of the log files. Eg if filename_prefix is "dummy",
            name of log files are dummymetric.jsonl, dummylog.jsonl etc.
            This argument is ignored if `filename` is set. Defaults to "".

        Returns:
            Experiment
        """

        if filename is None:
            # We need to parse multiple files

            get_file_path = partial(
                filesystem.get_logger_file_path,
                logger_dir=logger_dir,
                filename=filename,
                filename_prefix=filename_prefix,
            )

            config_file_path = get_file_path(filename_suffix="config_log")
            metric_file_path = get_file_path(filename_suffix="metric_log")

            config = self.config_parser.get_one_config(file_path=config_file_path)
            metrics = self.metric_parser.get_metrics_as_df(file_path=metric_file_path)

        else:
            # We need to parse just one file
            get_file_path = partial(
                filesystem.get_logger_file_path,
                logger_dir=logger_dir,
                filename=filename,
                filename_prefix=filename_prefix,
            )

            log_file_path = get_file_path(filename_suffix="log",)

            config = self.config_parser.get_one_config(file_path=log_file_path)
            metrics = self.metric_parser.get_metrics_as_df(file_path=log_file_path)

        assert config is not None
        return Experiment(config=config, metrics=metrics, logger_dir=logger_dir)

    def get_experiment_sequence(
        self,
        logger_path: str,
        filename: Optional[str] = None,
        filename_prefix: str = "",
    ) -> ExperimentSequence:
        """Load a sequence of experiments frrom the log dirs.

        Args:
            logger_dir (str): Path where the logs will be read from.
            filename (Optional[str], optional): Name to assigned to the
            log file (eg log.jsonl). If None is passed, this argument is
            ignored and it is assumed that multiple log files are written
            per experiment (for config, metadata, metric etc).  If the
            value is set, `filename_prefix` argument is ignored. Defaults
            to None.
            filename_prefix (str, optional): String to prefix before the
            name of the log files. Eg if filename_prefix is "dummy",
            name of log files are dummymetric.jsonl, dummylog.jsonl etc.
            This argument is ignored if `filename` is set. Defaults to "".

        Returns:
            ExperimentSequence
        """

        experiments = []
        for current_dir in Path(logger_path).iterdir():
            if current_dir.is_dir():
                experiments.append(
                    self.get_one_experiment(
                        logger_dir=str(current_dir),
                        filename=filename,
                        filename_prefix=filename_prefix,
                    )
                )
        return ExperimentSequence(experiments=experiments)
