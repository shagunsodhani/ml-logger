"""Implementation of the LogBook class.

LogBook class provides an interface to persist the logs on the filesystem,
tensorboard, remote backends, etc.

"""

import importlib
import time
from copy import deepcopy
from typing import Any, List, Optional

from ml_logger.logger.base import Logger as LoggerType
from ml_logger.types import ConfigType, KeyMapType, LogType, MetricType


class LogBook:
    """This class provides an interface to persist the logs on the filesystem, tensorboard, remote backends, etc."""

    def __init__(self, config: ConfigType):
        """Initialise the Logbook class.

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
        self.time_format = "%I:%M:%S%p %Z %b %d, %Y"  # 10:21:14PM EST Mar 04, 2020
        self.loggers: List[LoggerType] = []
        for logger_name, logger_config in config["loggers"].items():
            logger_module = importlib.import_module(f"ml_logger.logger.{logger_name}")
            logger_cls = getattr(logger_module, "Logger")
            logger = logger_cls(config=logger_config)
            self.loggers.append(logger)

    def _process_log(self, log: LogType, log_type: str) -> LogType:
        """Process the log before writing.

        Args:
            log (LogType): Log to process
            log_type (str): Type of the log: config, metric, metadata, etc

        Returns:
            LogType: Processed log
        """
        log["logbook_id"] = self.id
        log["logbook_timestamp"] = time.strftime(self.time_format)
        log["logbook_type"] = log_type
        return log

    def write(self, log: LogType, log_type: str = "metric") -> None:
        """Write log to loggers.

        Args:
            log (LogType): Log to write
            log_type (str, optional): Type of this log. Defaults to "metric".
        """
        log = self._process_log(deepcopy(log), log_type)
        for logger in self.loggers:
            logger.write(log=log)

    def write_config(self, config: ConfigType) -> None:
        """Write config to loggers.

        Args:
            config [ConfigType]: Config to write.
        """
        return self.write(log=config, log_type="config")

    def write_metric(self, metric: MetricType) -> None:
        """Write metric to loggers.

        Args:
            metric (MetricType): Metric to write
        """
        return self.write(log=metric, log_type="metric")

    def write_message(self, message: Any, log_type: str = "info") -> None:
        """Write message string to loggers.

        Args:
            message (Any): Message string to write
            log_type (str, optional): Type of this message (log).
                Defaults to "info".
        """
        return self.write(log={"message": message}, log_type=log_type)

    def write_metadata(self, metadata: LogType) -> None:
        """Write metadata to loggers.

        Args:
            metadata (LogType): Metadata to wite
        """
        return self.write(log=metadata, log_type="metadata")


def make_config(
    id: str = "0",
    name: str = "default_logger",
    write_to_console: bool = True,
    logger_dir: Optional[str] = None,
    filename: Optional[str] = None,
    filename_prefix: str = "",
    create_multiple_log_files: bool = True,
    wandb_config: Optional[ConfigType] = None,
    wandb_key_map: Optional[KeyMapType] = None,
    wandb_prefix_key: Optional[str] = None,
    tensorboard_config: Optional[ConfigType] = None,
    tensorboard_key_map: Optional[KeyMapType] = None,
    tensorboard_prefix_key: Optional[str] = None,
    mlflow_config: Optional[ConfigType] = None,
    mlflow_key_map: Optional[KeyMapType] = None,
    mlflow_prefix_key: Optional[str] = None,
    mongo_config: Optional[ConfigType] = None,
) -> ConfigType:
    """Make the config that can be passed to the LogBook constructor.

    Args:
        id (str, optional): Id of the current LogBook instance. Defaults to "0".
        name (str, optional): Name of the logger. Defaults to "default_logger".
        write_to_console (bool, optional): Should write the logs to console.
            Defaults to True
        logger_dir (str, optional):  Path where the logs will be
            written. If None is passed, logs are not written to the filesystem.
            LogBook creates the directory, if it does not exist. Defaults
            to None.
        filename (str, optional):  Name to assign to the log file (eg
            log.jsonl). If None is passed, this argument is ignored. If
            the value is set, `filename_prefix` and `create_multiple_log_files`
            arguments are ignored. Defaults to None.
        filename_prefix (str): String to prefix before the name of the log
            files. Eg if filename_prefix is "dummy", name of log files are
            dummymetric.jsonl, dummylog.jsonl etc. This argument is ignored
            if `filename` is set. Defaults to "".
        create_multiple_log_files (bool, optional): Should multiple log
            files be created - for config, metric, metadata and message
            logs. If True, the files are named as config_log.jsonl,
            metric_log.jsonl etc. If False, only one file log.jsonl is
            created. This argument is ignored if `filename` is set.
            Defaults to True.
        wandb_config (Optional[ConfigType], optional): Config for the wandb
            logger. If None, wandb logger is not created. The config can
            have any parameters that wandb.init() methods accepts
            (https://docs.wandb.com/library/init). Note that the wandb_config
            is passed as keyword arguments to the wandb.init() method.
            This provides a lot of flexibility to the users to configure
            wandb. This also means that the config should not have any
            parameters that wandb.init() would not accept. Defaults to None.
        wandb_key_map (Optional[KeyMapType], optional): When using wandb
            logger for logging metrics, certain keys are required. This
            dictionary provides an easy way to map the keys in the `log`
            to be written) with the keys that wandb logger needs. For
            instance, wandb logger needs a `step` key in all the metric
            logs. If your logs have a key called `epoch` that you want to
            use as `step`, set `wandb_key_map` as `{epoch: step}`. This
            argument is ignored if set to None. Defaults to None.
        wandb_prefix_key (Optional[str], optional): When a metric is logged
            to wandb, prefix the value (corresponding to the key) to all
            the remaining keys before values are logged in the wandb logger.
            This argument is ignored if set to None. Defaults to None.
        tensorboard_config (Optional[ConfigType], optional): config to
            initialise the tensorboardX logger. The config can have
            any parameters that [tensorboardX.SummaryWriter() method](https://tensorboardx.readthedocs.io/en/latest/tensorboard.html#tensorboardX.SummaryWriter)
            accepts. Note that the config is passed as keyword arguments
            to the tensorboardX.SummaryWriter() method. This provides a lot
            of flexibility to the users to configure tensorboard. This also
            means that config should not have any parameters that
            tensorboardX.SummaryWriter() would not accept. Defaults to None.
        tensorboard_key_map (Optional[KeyMapType], optional): When using
            tensorboard logger for logging metrics, certain keys are required.
            This dictionary provides an easy way to map the keys in the `log`
            (to be written) with the keys that tensorboard logger needs.
            For instance, tensorboard logger needs a `main_tag` key and a
            `global_step` in all the metric logs. If your logs have a key
            called `epoch` that you want to use as `step`, and a key called
            `mode` that you want to use as `main_tag`, set `tensorboard_key_map`
            as `{epoch: global_step, mode: main_tag}`. This argument is
            ignored if set to None. Defaults to None.
        tensorboard_prefix_key (Optional[str], optional): When a metric is
            logged to tensorboard, prefix the value (corresponding to the key)
            to all the remaining keys before values are logged in the
            tensorboard logger. This argument is ignored if set to None.
            Defaults to None.
        mlflow_config (Optional[ConfigType], optional): config to
            initialise an mlflow experiment. The config can have
            any parameters that [mlflow.create_experiment() method](https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.create_experiment)
            accepts. Note that the config is passed as keyword arguments
            to the mlflow.create_experiment() method. This provides a lot
            of flexibility to the users to configure mlflow. This also
            means that config should not have any parameters that
            mlflow.create_experiment would not accept. Defaults to None.
        mlflow_key_map (Optional[KeyMapType], optional): When using mlflow
            logger for logging metrics, certain keys are required. This
            dictionary provides an easy way to map the keys in the `log`
            (to be written) with the keys that mlflow logger needs. For
            instance, mlflow logger needs a `step` key in all the metric
            logs. If your logs have a key called `epoch` that you want to
            use as `step`, set `mlflow_key_map` as `{epoch: step}`. This
            argument is ignored if set to None. Defaults to None.
        mlflow_prefix_key (Optional[str], optional): When a metric is logged
            to mlflow, prefix the value (corresponding to the key) to all
            the remaining keys before values are logged in the mlflow logger.
            This argument is ignored if set to None. Defaults to None.
        mongo_config (Optional[ConfigType], optional): config to
            initialise connection to a collection in mongodb. The config
            supports the following keys:
                (1) host: host where mongodb is running.
                (2) port: port on which mongodb is running.
                (3) db: name of the db to use.
                (4) collection: name of the collection to use.
            Defaults to None.

    Returns:
        ConfigType: config to construct the LogBook
    """
    loggers: ConfigType = {}
    if logger_dir is not None:
        loggers["filesystem"] = {
            "logger_dir": logger_dir,
            "logger_name": name,
            "write_to_console": write_to_console,
            "filename": filename,
            "create_multiple_log_files": create_multiple_log_files,
            "filename_prefix": filename_prefix,
        }
        loggers["filesystem"]["logbook_key_map"] = None
        loggers["filesystem"]["logbook_key_prefix"] = None
    if wandb_config is not None:
        loggers["wandb"] = wandb_config
        loggers["wandb"]["logbook_key_map"] = wandb_key_map
        loggers["wandb"]["logbook_key_prefix"] = wandb_prefix_key

    if tensorboard_config is not None:
        loggers["tensorboard"] = tensorboard_config
        loggers["tensorboard"]["logbook_key_map"] = tensorboard_key_map
        loggers["tensorboard"]["logbook_key_prefix"] = tensorboard_prefix_key

    if mlflow_config is not None:
        loggers["mlflow"] = mlflow_config
        loggers["mlflow"]["logbook_key_map"] = mlflow_key_map
        loggers["mlflow"]["logbook_key_prefix"] = mlflow_prefix_key

    if mongo_config is not None:
        key = "mongo"
        loggers[key] = mongo_config
        loggers[key]["logbook_key_map"] = None
        loggers[key]["logbook_key_prefix"] = None

    config = {"id": id, "name": name, "loggers": loggers}
    return config
