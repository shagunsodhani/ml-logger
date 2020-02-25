"""
Implementation of the LogBook class.

LogBook class provides an interface to persist the logs on filesystem,
tensorboard, remote backends etc.

"""

import importlib
import time
from typing import List, Optional

from ml_logger.logger.base import Logger as LoggerType
from ml_logger.types import ConfigType, LogType, MetricType


class LogBook:
    """This class provides an interface to persist the logs on filesystem,
    tensorboard, remote backends etc.

    """

    def __init__(self, config: ConfigType):
        """Initialise the Logbook class

        Args:
            logbook_config (ConfigType): Config to initialise the
                LogBook class. The logbook config must have the
                following keys:
                id: Id of the current LogBook instance. This
                    attribute is logged with each log and is useful
                    when multiple LogBook instances are needed (for
                    example with multiprocessing)
                logger_file_path: Path to the file, where the logs
                    will be written
                The logbook config can be created using the make_config
                method defined in ml_logger/logbook.py
            config (ConfigType): config corresponding to the ml experiment
                creating the logbook
        """
        self.id = config["id"]
        self.logger_name = config["name"]
        self.loggers: List[LoggerType] = []
        for logger_name, logger_config in config["loggers"].items():
            logger_module = importlib.import_module(f"ml_logger.logger.{logger_name}")
            logger_cls = getattr(logger_module, "Loggger")
            logger = logger_cls(config=logger_config)
            self.loggers.append(logger)

    def _process_log(self, log: LogType, log_type: str) -> LogType:
        """Process the log before writing

        Args:
            log (LogType): Log to process
            log_type (str): Type of the log: config, metric, metadata, etc

        Returns:
            LogType: Processed log
        """

        log["logbook_id"] = self.id
        log["logbook_timestamp"] = time.strftime("%I:%M%p %Z %b %d, %Y")
        log["logbook_type"] = log_type
        return log

    def write_log(self, log: LogType, log_type: str = "metric",) -> None:
        """Write log to loggers

        Args:
            log (LogType): Log to write
            log_type (str, optional): Type of this log. Defaults to "metric".
        """

        log = self._process_log(log, log_type)
        for logger in self.loggers:
            logger.write_log(log=log)

    def write_config_log(self, config: ConfigType,) -> None:
        """Write config to loggers

        Args:
            config [ConfigType]: Config to write.
        """
        return self.write_log(log=config, log_type="config")

    def write_metric_log(self, metric: MetricType,) -> None:
        """Write metric to loggers

        Args:
            metric (MetricType): Metric to write
        """
        return self.write_log(log=metric, log_type="metric")

    def write_message(self, message: str) -> None:
        """Write message string to loggers

        Args:
            message (str): Message string to write
        """
        return self.write_log(log={"messgae": message}, log_type="message")

    def write_metadata_log(self, metadata: LogType,) -> None:
        """Write metadata to loggers

        Args:
            metadata (LogType): Metadata to wite
        """
        return self.write_log(log=metadata, log_type="metadata")


def make_config(
    id: str = "0",
    name: str = "default_logger",
    logger_file_path: Optional[str] = None,
    wandb_config: Optional[ConfigType] = None,
) -> ConfigType:
    """Make the config that can be passed to the LogBook constructor

    Args:
        id (str, optional): Id of the current LogBook instance. Defaults to "0".
        name (str, optional): Name of the logger. Defaults to "default_logger".
        logger_file_path (str, optional):  Path where the logs will be
            written. If None is pass, logs are not written to the filesystem.
            Defaults to None.
        wandb_config (Optional[ConfigType], optional): Config for the wandb
            logger. If None, wandb logger is not created. The config can
            have any parameters that wandb.init() methods accepts
            (https://docs.wandb.com/library/init). Note that the wandb_config
            is passed as keyword arguments to the wandb.init() method.
            This provides a lot of flexibility to the users to configure
            wandb. This also means that config should not have any
            parameters that wandb.init() would not accept.Defaults to None.

    Returns:
        ConfigType: config to construct the LogBook
    """
    loggers = {}
    if logger_file_path is not None:
        loggers["filesystem"] = {
            "logger_file_path": logger_file_path,
            "logger_name": name,
        }
    if wandb_config is not None:
        loggers["wandb"] = wandb_config

    config = {"id": id, "name": name, "loggers": loggers}
    return config
