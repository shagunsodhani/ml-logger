"""Container for the experiment data"""

from collections.abc import Sequence
from typing import Any, Callable, Dict, List, Optional, Union, overload

import pandas as pd

from ml_logger.types import LogType


class Experiment:
    def __init__(
        self,
        config: LogType,
        metrics: Dict[str, pd.DataFrame],
        info: Optional[Dict[Any, Any]] = None,
    ):
        """Class to hold the experiment data

        Args:
            config (LogType): Config used for the experiment
            metrics (Dict[str, pd.DataFrame]): Dictionary mapping strings
                to dataframes. Keys could be "train", "validation", "test"
                and corresponding dataframes would have the data for these
                modes.
            info (Dict[Any, Any]): A dictionary where the user can store
                any information about the experiment (that does not fit
                within config and metrics).
        """
        self.config = config
        self.metrics = metrics
        self.info: Dict[Any, Any] = {}
        if info is not None:
            self.info = info


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
        return self.experiments[index]

    def __len__(self) -> int:
        return len(self.experiments)
