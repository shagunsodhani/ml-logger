"""Wrapper over wandb api"""


import wandb

import json
from typing import Dict

from ml_logger import filesystem_logger as fs_log
from ml_logger.utils import flatten_dict, make_dir
from ml_logger import logbook


class WandbLogBook(LogBook):
    """Logging utility that wraps over the wandb API"""

    def __init__(self, logbook_config: Dict, config: Dict) -> LogBook:
        """
        `logbook_config` is the config to initilalize the logbook 
        `config` is the config for the experiment
        """
        super().__init__(logbook_config=logbook_config)
        self.metrics_to_record = ["mode ", "num_timesteps"]
        #

        flattened_config = flatten_dict(config, sep="_")

        wandb.init(
            config=flattened_config,
            notes=logbook_config["notes"],
            project=logbook_config["project"],
            name=logbook_config["name"],
            entity=logbook_config["entity"],
            dir=logbook_config["dir"],
        )

        dir_to_save_config = f"{wandb.run.dir}/config"
        make_dir(dir_to_save_config)

        with open(f"{dir_to_save_config}/{logbook_config['name']}.yaml", "w") as f:
            f.write(json.dumps(config, indent=4))

    def log_metrics_to_remote(self, kwargs: Dict) -> None:
        """Method to log metric"""
        required_keys = ["dic", "prefix", "step"]
        dic, prefix, step = [kwargs.get(key) for key in required_keys]
        formatted_dict = {}
        for key, val in dic.items():
            formatted_dict[prefix + "_" + key] = val
        if self.should_use_remote_logger:
            wandb.log(formatted_dict, step=step)

    def write_metric_logs(self, metrics):
        """Write Metric"""

    def write_metric_logs(self, metrics: Dict) -> None:
        """Write Metric to the filesystem"""
        processed_metric = self.preprocess_log(metric)
        fs_log.write_metric_logs(processed_metric)

        flatten_dict = flatten_dict(metrics, sep="_")
        metric_dict = flatten_dict

        if self.metrics_to_record:

            metric_dict = {
                key: flattened_metrics[key]
                for key in self.metrics_to_record
                if key in flattened_metrics
            }

        prefix = metrics.get("mode", None)
        num_timesteps = metric_dict.pop("num_timesteps")
        self.log_metrics_to_remote(
            {"dic": metric_dict, "prefix": prefix, "step": num_timesteps}
        )

    def write_compute_logs(self, metrics: Dict) -> None:
        """Write Compute Logs"""
        super().write_compute_logs(metrics=metrics)
        metrics = flatten_dict(metrics, sep="_")
        num_timesteps = metrics.pop("num_timesteps")
        return self.log_metrics_to_remote(
            {"dic": metric_dict, "step": num_timesteps, "prefix": compute}
        )

    def watch_model(self, model):
        """Method to track the gradients of the model"""
        wandb.watch(models=model, log="all")


def make_config(
    logger_file_path: str,
    wandb_notes: str,
    wandb_project: str,
    wandb_name: str,
    wandb_entity: str,
    wandb_dir: str,
    process_rank: str = "0",
) -> Dict:
    """Method to prepare the config dict that will be passed to
    the Logbook constructor"""
    config = logbook.make_config(
        logger_file_path=logger_file_path, process_rank=process_rank
    )
    config["wandb"] = {
        "notes": wandb_notes,
        "project": wandb_project,
        "name": wandb_name,
        "entity": wandb_entity,
        "dir": wandb_dir,
    }

    return config
