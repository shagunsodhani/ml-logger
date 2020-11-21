"""Container for the experiment data."""

from collections import UserList
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
from ml_logger.types import LogType


class Experiment:
    def __init__(
        self,
        configs: List[LogType],
        metrics: Dict[str, pd.DataFrame],
        info: Optional[Dict[Any, Any]] = None,
    ):
        """Class to hold the experiment data.

        Args:
            config (Optional[LogType]): Config used for the experiment
            metrics (Dict[str, pd.DataFrame]): Dictionary mapping strings
                to dataframes. Keys could be "train", "validation", "test"
                and corresponding dataframes would have the data for these
                modes.
            info (Optional[Dict[Any, Any]], optional): A dictionary where the user can store
                any information about the experiment (that does not fit
                within config and metrics). Defaults to None.
        """
        self.configs = configs
        self.metrics = metrics
        self.info: Dict[Any, Any] = {}
        if info is not None:
            self.info = info

    @property
    def config(self) -> Optional[LogType]:
        """Access the config property."""
        if len(self.configs) > 0:
            return self.configs[-1]
        return None


class ExperimentSequence(UserList):  # type: ignore
    def __init__(self, experiments: List[Experiment]):
        """List-like interface to a collection of Experiments."""
        super().__init__(experiments)

    def groupby(
        self, group_fn: Callable[[Experiment], str]
    ) -> Dict[str, "ExperimentSequence"]:
        """Group experiments in the sequence.

        Args:
            group_fn: Function to assign a string group id to the experiment

        Returns:
            Dict[str, ExperimentSequence]: A dictionary mapping the sring
            group id to a sequence of experiments
        """
        grouped_experiments: Dict[str, List[Experiment]] = {}
        for experiment in self.data:
            key = group_fn(experiment)
            if key not in grouped_experiments:
                grouped_experiments[key] = []
            grouped_experiments[key].append(experiment)

        return {
            key: ExperimentSequence(value) for key, value in grouped_experiments.items()
        }

    def filter(self, filter_fn: Callable[[Experiment], bool]) -> "ExperimentSequence":
        """Filter experiments in the sequence.

        Args:
            filter_fn: Function to filter an experiment

        Returns:
            ExperimentSequence: A sequence of experiments for which the
            filter condition is true
        """
        return ExperimentSequence(
            [experiment for experiment in self.data if filter_fn(experiment)]
        )
