"""Implementation of the `WandbLogBook` class

This class provides an interface to persist the logs on Wandb and
filesystem
"""

import json
from typing import List, Optional, cast

import wandb
from ml_logger import logbook, utils
from ml_logger.types import ConfigType, MetricType, ModelType


class WandbLogBook(logbook.LogBook):
    """This class provides an interface for the experiments to persist
        logs to Wandb and filesystem

    Args:
        logbook ([type]): This class provides an interface to perist the
            logs to the filesystem
    """

    def __init__(
        self,
        logbook_config: ConfigType,
        config: ConfigType,
        metrics_to_log_remotely: Optional[List[str]] = None,
    ):
        """Initialise the `WandbLogBook` class

        Args:
            logbook_config (ConfigType): Config to initialise the
                `WandbLogBook` class. The logbook config must have the
                following keys:
                * `logger_file_path`: Path to the file, where the
                    logs will be written
                * `logging_idx_key`: The key (in `log`) to use as the
                    `step` key for wandb
                    Refer https://docs.wandb.com/library/python/log
                * `wandb_notes`:
                    Refer https://docs.wandb.com/library/python/init
                * `wandb_project`:
                    Refer https://docs.wandb.com/library/python/init
                * `wandb_name`:
                    Refer https://docs.wandb.com/library/python/init
                * `wandb_entity`:
                    Refer https://docs.wandb.com/library/python/init
                * `wandb_dir`:
                    Refer https://docs.wandb.com/library/python/init
                * `id`: Id of the current `LogBook` instance
                * `logger_name`: Name of the logger
            config (ConfigType): config corresponding to the ml experiment
                creating the logbook
            metrics_to_log_remotely (List[str]): Name of the metrics that
                will be logged in wandb. If None is passed, all metrics
                are logged. Defaults to None
        """
        super().__init__(logbook_config=logbook_config, config=config)
        self.logging_idx_key = logbook_config["logging_idx_key"]
        self.metrics_to_log_remotely = metrics_to_log_remotely

        flattened_config = utils.flatten_dict(d=config, sep="_")

        wandb.init(
            config=flattened_config,
            notes=logbook_config["wandb"]["notes"],
            project=logbook_config["wandb"]["project"],
            name=logbook_config["wandb"]["name"],
            entity=logbook_config["wandb"]["entity"],
            dir=logbook_config["wandb"]["dir"],
        )

        dir_to_save_config = f"{wandb.run.dir}/config"
        utils.make_dir(path=dir_to_save_config)

        with open(
            f"{dir_to_save_config}/{logbook_config['wandb']['name']}.yaml", "w"
        ) as f:
            f.write(json.dumps(config, indent=4))

    def _log_metric_to_remote(self, metric: MetricType, metadata: ConfigType) -> None:
        """Log metric to remote backend

        Args:
            metric (MetricType): metric to log
            metadata (ConfigType): metadata that is used to interface
                with the remote backend
        """
        prefix = cast("str", metric.get("prefix"))
        step = cast("int", metric.get("step"))
        formatted_metric: MetricType = {}
        if prefix == "":
            formatted_metric = metric
        else:
            for key, val in metric.items():
                formatted_metric[prefix + "_" + key] = val
        wandb.log(formatted_metric, step=step)

    def write_metric_log(self, metric: MetricType) -> None:
        """Write metric log to filesystem and wandb

        Args:
            metric (MetricType): metric to write

        """
        processed_metric = self._process_log(log=metric)
        super().write_metric_log(metric=processed_metric)
        if self.metrics_to_log_remotely is not None:
            metric_to_log = {
                key: metric[key]
                for key in self.metrics_to_log_remotely
                if key in metric
            }
        else:
            metric_to_log = metric
        prefix = metric.get("mode", "")
        logging_idx = metric.pop(self.logging_idx_key)
        self._log_metric_to_remote(
            metric=metric_to_log, metadata={"prefix": prefix, "step": logging_idx}
        )

    def write_compute_log(self, metric: MetricType) -> None:
        """Write compute log to filesystem and wandb

        Args:
            metric (MetricType): Compute metric to write

        """
        super().write_compute_log(metric=metric)
        num_timesteps = metric.pop("num_timesteps")
        self._log_metric_to_remote(
            metric=metric, metadata={"step": num_timesteps, "prefix": "compute"}
        )

    def watch_model(self, model: ModelType) -> None:
        """Track the gradients of the model

        Args:
            model (ModelType): model to track gradients of
        """

        wandb.watch(models=model, log="all")


def make_config(
    logger_file_path: str,
    logging_idx_key: str,
    wandb_notes: str,
    wandb_project: str,
    wandb_name: str,
    wandb_entity: str,
    wandb_dir: str,
    id: str = "0",
    logger_name: str = "default_logger",
) -> ConfigType:
    """Make a config that can be passed to the `WandbLogBook` constructor

    Args:
        logger_file_path (str): Path to the file, where the logs
            will be written
        logging_idx_key (str): The key (in `log`) to use as the `step` key
            for wandb. Refer https://docs.wandb.com/library/python/log
        wandb_notes (str): Refer https://docs.wandb.com/library/python/init
        wandb_project (str): Refer https://docs.wandb.com/library/python/init
        wandb_name (str): Refer https://docs.wandb.com/library/python/init
        wandb_entity (str): Refer https://docs.wandb.com/library/python/init
        wandb_dir (str): Refer https://docs.wandb.com/library/python/init
        id (str, optional): Id of the current `LogBook` instance. Defaults
            to "0"
        logger_name (str, optional): Name of the logger. Defaults to
            "default_logger"

    Returns:
        ConfigType: `config` to construct the `WandbLogBook`
    """
    config = logbook.make_config(
        logger_file_path=logger_file_path, id=id, logger_name=logger_name,
    )
    config["logging_idx_key"] = logging_idx_key
    config["wandb"] = {
        "notes": wandb_notes,
        "project": wandb_project,
        "name": wandb_name,
        "entity": wandb_entity,
        "dir": wandb_dir,
    }

    return config
