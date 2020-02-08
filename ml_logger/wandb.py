"""Wrapper over wandb api"""


import json
from typing import Any, Dict, List, Optional, Union, cast

import wandb
from ml_logger import filesystem_logger as fs_log
from ml_logger import logbook, utils
from ml_logger.types import (
    ConfigType,
    LogType,
    MetricType,
    ModelType,
    RemoteMetricType,
    ValueType,
)


class WandbLogBook(logbook.LogBook):
    """Logging utility that wraps over the wandb API"""

    def __init__(self, logbook_config: ConfigType, config: ConfigType):
        """
        `logbook_config` is the config to initilalize the logbook 
        `config` is the config for the experiment
        """
        super().__init__(logbook_config=logbook_config, config=config)
        self.metrics_to_record: List[str] = []

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
        """Method to log metric"""
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
        """Write Metric to the filesystem and wandb"""
        processed_metric = self.process_log(log=metric)
        fs_log.write_metric_log(metric=processed_metric)
        if self.metrics_to_record:
            metric_to_log = {
                key: metric[key] for key in self.metrics_to_record if key in metric
            }
        else:
            metric_to_log = metric
        prefix = metric.get("mode", "")
        logging_idx = metric.pop(self.logging_idx_key)
        self._log_metric_to_remote(
            metric=metric_to_log, metadata={"prefix": prefix, "step": logging_idx}
        )

    def write_compute_log(self, metric: MetricType) -> None:
        """Write Compute Log"""
        super().write_compute_log(metric=metric)
        num_timesteps = metric.pop("num_timesteps")
        self._log_metric_to_remote(
            metric=metric, metadata={"step": num_timesteps, "prefix": "compute"}
        )

    def watch_model(self, model: ModelType) -> None:
        """Method to track the gradients of the model"""
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
    """Method to prepare the config dict that will be passed to
    the Logbook constructor"""
    config = logbook.make_config(
        logger_file_path=logger_file_path,
        id=id,
        logging_idx_key=logging_idx_key,
        logger_name=logger_name,
    )
    config["wandb"] = {
        "notes": wandb_notes,
        "project": wandb_project,
        "name": wandb_name,
        "entity": wandb_entity,
        "dir": wandb_dir,
    }

    return config
