import time
from typing import Optional

from ml_logger import filesystem_logger as fs_log
from ml_logger.types import ConfigType, LogType, MetricType


class LogBook:
    """Logging utility for ML Experiments"""

    def __init__(self, logbook_config: ConfigType, config: ConfigType):
        self.id = logbook_config["id"]
        self.logger_name = logbook_config["name"]
        fs_log.set_logger(
            logger_file_path=logbook_config["logger_file_path"],
            logger_name=self.logger_name,
        )

        self.logging_idx_key = logbook_config["logging_idx_key"]
        self.config = config
        # self.tensorboard_writer = None
        # self.should_use_tb = config.logger.tensorboard.should_use
        # if self.should_use_tb:
        #     self.tensorboard_writer = SummaryWriter(comment=config.logger.project_name)

    def _log_metric_to_remote(self, metric: MetricType, metadata: ConfigType) -> None:
        """Method to log the metric to remote backend"""
        pass

    def process_log(self, log: LogType) -> LogType:
        """"Method to preprocess the log before logging"""
        log["id"] = self.id
        log["timestamp"] = time.strftime("%I:%M%p %Z %b %d, %Y")
        return log

    def write_config_log(self, config: Optional[ConfigType] = None) -> None:
        """Write config"""
        if config is None:
            config = self.config
        processed_config = self.process_log(log=config)
        fs_log.write_config_log(processed_config, logger_name=self.logger_name)

    def write_metric_log(self, metric: MetricType) -> None:
        """Write Metric to the filesystem"""
        processed_metric = self.process_log(log=metric)
        fs_log.write_metric_log(metric=processed_metric, logger_name=self.logger_name)
        # if self.should_use_tb:

        #     timestep_key = "num_timesteps"
        #     for key in set(list(metrics.keys())) - set([timestep_key]):
        #         self.tensorboard_writer.add_scalar(
        #             tag=key,
        #             scalar_value=metrics[key],
        #             global_step=metrics[timestep_key],
        #         )

    def write_compute_log(self, metric: MetricType) -> None:
        """Write Compute Log"""
        return self.write_metric_log(metric=metric)

    def write_message_log(self, message: str) -> None:
        """Write message log"""
        unprocessed_log: LogType = {"messgae": message}
        message_log = self.process_log(log=unprocessed_log)
        fs_log.write_message_log(message_log=message_log, logger_name=self.logger_name)

    def write_metadata_log(self, metadata: LogType) -> None:
        """Write metadata"""
        processed_metadata = self.process_log(log=metadata)
        fs_log.write_metadata_log(processed_metadata, logger_name=self.logger_name)


def make_config(
    logger_file_path: str,
    id: str = "0",
    logging_idx_key: str = "minibatch_idx",
    logger_name: str = "default_logger",
    use_multiprocessing_logging: bool = False,
) -> ConfigType:
    """Method to prepare the config dict that will be passed to
    the Logbook constructor.
    `id` flag is useful when using multi-processing"""
    config = {
        "id": id,
        "logger_file_path": logger_file_path,
        "logging_idx_key": logging_idx_key,
        "name": logger_name,
    }
    return config
