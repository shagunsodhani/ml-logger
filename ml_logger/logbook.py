"""Implementation of the `LogBook` class

This class provides an interface to persist the logs on the filesystem

"""
import time
from typing import List, NoReturn, Optional

from ml_logger import filesystem_logger as fs_log
from ml_logger.types import ConfigType, LogType, MetricType


class LogBook:
    """This class provides an interface for the experiments to persist
        logs on the filesystem

    """

    def __init__(self, logbook_config: ConfigType, config: ConfigType):
        """Initialise the `Logbook` class

        Args:
            logbook_config (ConfigType): Config to initialise the
                `LogBook` class. The logbook config must have the
                following keys:
                * `id`: Id of the current `LogBook` instance. This
                    attribute is logged with each `log` and is useful
                    when multiple `LogBook` instances are needed (for
                    example with multiprocessing)
                * `logger_file_path`: Path to the file, where the logs
                    will be written
                The logbook config can be created using the `make_config`
                method defined in `ml_logger/logbook.py`
            config (ConfigType): config corresponding to the ml experiment
                creating the logbook
        """
        self.id = logbook_config["id"]
        self.logger_name = logbook_config["name"]
        fs_log.set_logger(
            logger_file_path=logbook_config["logger_file_path"],
            logger_name=self.logger_name,
        )
        self.config = config

    def _log_metric_to_remote(
        self, metric: MetricType, metadata: ConfigType
    ) -> NoReturn:
        """Log metric to remote backend

        Args:
            metric (MetricType): metric to log
            metadata (ConfigType): metadata that is used to interface
                with the remote backend

        Raises:
            NotImplementedError: This method is not implemented for the
                `LogBook` class but maybe implemented by the classes
                that subclass it.
        """

        raise NotImplementedError(
            "_log_metric_to_remote() is not implemented for LogBook"
        )

    def _process_log(self, log: LogType) -> LogType:
        """Process the log before writing

        Args:
            log (LogType): `log` to process

        Returns:
            LogType: `log` with the following additional fields:
                * `id`: `id` of the current `LogBook` instance
                * `timestamp`: current timestamp
        """
        log["id"] = self.id
        log["timestamp"] = time.strftime("%I:%M%p %Z %b %d, %Y")
        return log

    def write_log(
        self,
        log: LogType,
        keys_to_serialize: Optional[List[str]] = None,
        log_type: str = "metric",
    ) -> None:
        """Write log to filesystem

        Args:
            log (LogType): log to write
            keys_to_serialize (Optional[List[str]], optional): keys
                (in log) to serialize. If None is passed, all the keys are
                serialized. Defaults to None.
            log_type (str, optional): `type` of this log. Defaults to "metric"

        """

        return fs_log.serialize_and_write_log(
            log=self._process_log(log=log),
            keys_to_serialize=keys_to_serialize,
            log_type=log_type,
            logger_name=self.logger_name,
        )

    def write_config_log(self, config: Optional[ConfigType] = None) -> None:
        """Write config to filesystem

        Args:
            config (Optional[ConfigType], optional): Config to write.
                Defaults to None.
        """
        if config is None:
            config = self.config

        return self.write_log(log=config, keys_to_serialize=None, log_type="config")

    def write_metric_log(self, metric: MetricType) -> None:
        """Write metric to filesystem

        Args:
            metric (MetricType): Metric to write
        """
        return self.write_log(log=metric, keys_to_serialize=None, log_type="metric")

    def write_compute_log(self, metric: MetricType) -> None:
        """Write compute log to filesystem

        Args:
            metric (MetricType): Compute metric to write

        """
        return self.write_log(log=metric, keys_to_serialize=None, log_type="compute")

    def write_message_log(self, message: str) -> None:
        """Write message string to filesystem

        Args:
            message (str): Message string to write
        """
        return self.write_log(
            log={"messgae": message}, keys_to_serialize=None, log_type="message"
        )

    def write_metadata_log(self, metadata: LogType) -> None:
        """Write metadata log to filesystem

        Args:
            metadata (LogType): Metadata to wite
        """
        return self.write_log(log=metadata, keys_to_serialize=None, log_type="metadata")


def make_config(
    logger_file_path: str, id: str = "0", logger_name: str = "default_logger",
) -> ConfigType:
    """Make a config that can be passed to the `LogBook` constructor

    Args:
        logger_file_path (str): Path to the file, where the logs
            will be written
        id (str, optional): Id of the current `LogBook` instance. Defaults
            to "0"
        logger_name (str, optional): Name of the logger. Defaults to
            "default_logger"

    Returns:
        ConfigType: `config` to construct the `LogBook`
    """

    config = {
        "id": id,
        "logger_file_path": logger_file_path,
        "name": logger_name,
    }
    return config
