"""Logger class that writes to wandb"""

import mlflow

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType, MetricType


class Logger(BaseLogger):
    """Logger class that writes to mlflow
    """

    def __init__(self, config: ConfigType):
        """Initialise the mlflow Logger

        Args:
            config (ConfigType): config to initialise the mlflow logger.
                The config can have any parameters that mlflow.create_experiment() method
                accepts (https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.create_experiment).
                Note that the config is passed as keyword arguments to
                the mlflow.create_experiment() method. This provides a
                lot of flexibility to the users to configure mlflow.
                This also means that config should not have any parameters
                that mlflow.create_experiment() would not accept.
        """
        super().__init__(config=config)
        self.keys_to_skip = ["logbook_id", "logbook_type", "logbook_timestamp"]
        self.keys_to_check = ["step"]
        mlflow.create_experiment(**config)

    def write_log(self, log: LogType) -> None:
        """Write the log to mlflow

        Args:
            log (LogType): Log to write
        """
        logbook_type = log["logbook_type"]
        if logbook_type == "metric":
            log = self._prepare_metric_log_to_write(log=log)
            self.write_metric_log(metric=log)
        else:
            log = self._prepare_log_to_write(log=log)
            if logbook_type == "config":
                self.write_config(config=log)
            # Only metric logs and message logs are supported right now

    def write_metric_log(self, metric: MetricType) -> None:
        """Write metric to mlflow

        Args:
            metric (MetricType): Metric to write
        """
        for key in self.keys_to_check:  # type: ignore
            assert key in metric
        step = metric.pop("step")
        if self.key_prefix:
            prefix = {metric.pop(self.key_prefix)}
            metric = {f"{prefix}_{key}": value for key, value in metric.items()}
        mlflow.log_metrics(metric, step)

    def write_config(self, config: ConfigType) -> None:
        """Write the config to mlflow

        Args:
            config (ConfigType): Config to write
        """
        mlflow.log_params(config)
