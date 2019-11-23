import time
from typing import Dict, Optional

from ml_logger import filesystem_logger as fs_log


class LogBook:
    """Logging utility for ML Experiments"""

    def __init__(self, logbook_config: Dict, config: Dict) -> "LogBook":
        self.id = logbook_config["id"]
        self.logger_name = logbook_config["name"]
        fs_log.set_logger(
            logger_file_path=logbook_config["logger_file_path"],
            logger_name=self.logger_name,
            use_multiprocessing_logging=logbook_config["use_multiprocessing_logging"],
        )

        self.logging_idx_key = logbook_config["logging_idx_key"]
        self.config = config
        # self.tensorboard_writer = None
        # self.should_use_tb = config.logger.tensorboard.should_use
        # if self.should_use_tb:
        #     self.tensorboard_writer = SummaryWriter(comment=config.logger.project_name)

    def log_metrics_to_remote(self, kwargs: Dict) -> None:
        """Method to log the metrics to remote backend"""
        pass

    def preprocess_log(self, log: Dict) -> Dict:
        """"Method to preprocess the log before logging"""
        log["id"] = self.id
        log["timestamp"] = time.strftime("%I:%M%p %Z %b %d, %Y")
        return log

    def write_config_log(self, config: Optional[Dict] = None) -> None:
        """Write config"""
        if config is None:
            config = self.config
        processed_config = self.preprocess_log(config)
        fs_log.write_config_log(processed_config, logger_name=self.logger_name)

    def write_metric_logs(self, metrics: Dict) -> None:
        """Write Metric to the filesystem"""
        processed_metrics = self.preprocess_log(metrics)
        fs_log.write_metric_logs(processed_metrics, logger_name=self.logger_name)
        # if self.should_use_tb:

        #     timestep_key = "num_timesteps"
        #     for key in set(list(metrics.keys())) - set([timestep_key]):
        #         self.tensorboard_writer.add_scalar(
        #             tag=key,
        #             scalar_value=metrics[key],
        #             global_step=metrics[timestep_key],
        #         )

    def write_compute_logs(self, metrics: Dict) -> None:
        """Write Compute Logs"""
        return self.write_metric_logs(metrics=metrics)

    def write_message_logs(self, message: str) -> None:
        """Write message logs"""
        message = {"messgae": message}
        processed_message = self.preprocess_log(message)
        fs_log.write_message_logs(processed_message, logger_name=self.logger_name)

    def write_metadata_logs(self, metadata: Dict) -> None:
        """Write metadata"""
        processed_metadata = self.preprocess_log(metadata)
        fs_log.write_metadata_logs(processed_metadata, logger_name=self.logger_name)


def make_config(
    logger_file_path: str,
    id: str = "0",
    logging_idx_key: str = "minibatch_idx",
    logger_name: str = "default_logger",
    use_multiprocessing_logging: bool = False,
) -> Dict:
    """Method to prepare the config dict that will be passed to
    the Logbook constructor.
    `id` flag is useful when using multi-processing"""
    config = {
        "id": id,
        "logger_file_path": logger_file_path,
        "logging_idx_key": logging_idx_key,
        "name": logger_name,
        "use_multiprocessing_logging": use_multiprocessing_logging,
    }
    return config
