"""Container for the experiment data."""

import gzip
import json
from collections import UserList
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
from ml_logger import utils
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

    def serialize(self, dir_path: str) -> None:
        """Serialize the experiment data and store at `dir_path`.

        * configs are stored as jsonl (since there are only a few configs per experiment) in a file called `config.jsonl`.
        * metrics are stored in [`feather` format](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_feather.html).
        * info is stored in the gzip format.
        """
        utils.make_dir(dir_path)
        path_to_save = f"{dir_path}/config.jsonl"
        with open(path_to_save, "w") as f:
            for config in self.configs:
                f.write(json.dumps(config) + "\n")

        metric_dir = f"{dir_path}/metric"
        utils.make_dir(metric_dir)
        for key in self.metrics:
            path_to_save = f"{metric_dir}/{key}"
            if self.metrics[key].empty:
                pass
            else:
                self.metrics[key].to_feather(path=path_to_save)

        path_to_save = f"{dir_path}/info.gzip"
        with gzip.open(path_to_save, "wb") as f:  # type: ignore[assignment]
            f.write(json.dumps(self.info).encode("utf-8"))  # type: ignore[arg-type]

    def __eq__(self, other: object) -> bool:
        """Compare two `Experiment` objects"""
        if not isinstance(other, Experiment):
            return NotImplemented
        return (
            self.configs == other.configs
            and utils.compare_keys_in_dict(self.metrics, other.metrics)
            and all(
                self.metrics[key].equals(other.metrics[key]) for key in self.metrics
            )
            and utils.compare_keys_in_dict(self.info, other.info)
            and all(self.info[key] == other.info[key] for key in self.info)
        )


def deserialize(dir_path: str) -> Experiment:
    """Deserialize the experiment data stored at `dir_path` and return an Experiment object."""
    path_to_load_from = f"{dir_path}/config.jsonl"
    configs = []
    with open(path_to_load_from) as f:
        for line in f:
            configs.append(json.loads(line))

    metrics = {}
    dir_to_load_from = Path(f"{dir_path}/metric/")
    for path_to_load_metric in dir_to_load_from.iterdir():
        if path_to_load_metric.is_file():
            key = path_to_load_metric.parts[-1]
            metrics[key] = pd.read_feather(path_to_load_metric)
    if not metrics:
        metrics["all"] = pd.DataFrame()

    path_to_load_from = f"{dir_path}/info.gzip"
    with gzip.open(path_to_load_from, "rb") as f:  # type: ignore[assignment]
        info = json.loads(f.read().decode("utf-8"))  # type: ignore[attr-defined]

    return Experiment(configs=configs, metrics=metrics, info=info)


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
