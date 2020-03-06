"""Logger class that writes to wandb"""

from tensorboardX import SummaryWriter

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType, MetricType


class Logger(BaseLogger):
    """Logger class that writes to tensorboardX
    """

    def __init__(self, config: ConfigType):
        """Initialise the tensorboardX Logger

        Args:
            config (ConfigType): config to initialise the tensorboardX
                logger. The config can have any parameters that
                tensorboardX.SummaryWriter() method accepts
                (https://tensorboardx.readthedocs.io/en/latest/tensorboard.html#tensorboardX.SummaryWriter).
                Note that the config is passed as keyword arguments to the
                tensorboardX.SummaryWriter() method. This provides a lot
                of flexibility to the users to configure wandb. This also
                means that config should not have any parameters that
                tensorboardX.SummaryWriter() would not accept.
        """
        super().__init__(config=config)
        self.summary_writer = SummaryWriter(**config)
        self.keys_to_skip = ["logbook_id", "logbook_type", "logbook_timestamp"]

    def write_log(self, log: LogType) -> None:
        """Write the log to tensorboardX

        Args:
            log (LogType): Log to write
        """

        logbook_type = log["logbook_type"]
        log = self._prepare_log_to_write(log=log)

        if logbook_type == "metric":
            self.write_metric_log(metric=log)

        elif logbook_type == "config":
            self.write_config(config=log)
        else:
            pass
            # Only metric logs and configs can be written to tensorboardX

    def write_metric_log(self, metric: MetricType) -> None:
        """Write metric to tensorboard

        Args:
            metric (MetricType): Metric to write
        """
        global_step = None
        if "global_step" in metric:
            global_step = metric.pop("global_step")
        walltime = None
        if "walltime" in metric:
            walltime = metric.pop("walltime")

        main_tag = None
        if "tag" in metric:
            main_tag = metric.pop("tag")
        elif "main_tag" in metric:
            main_tag = metric.pop("main_tag")

        if self.key_prefix:
            prefix = {metric.pop(self.key_prefix)}
            metric = {f"{prefix}_{key}": value for key, value in metric.items()}

        for key, value in metric:
            self.summary_writer.add_scalar(
                tag=f"{main_tag}/key",
                value=value,
                global_step=global_step,
                walltime=walltime,
            )

    def write_config(self, config: ConfigType) -> None:
        """Write the config to tensorboard

        Args:
            config (ConfigType): Config to write
        """
        name = None
        if "name" in config:
            name = config.pop("name")

        metric_dict = None
        if "metric_dict" in config:
            metric_dict = config.pop("metric_dict")

        global_step = None
        if "global_step" in config:
            global_step = config.pop("global_step")

        self.summary_writer.add_hparams(
            hparam_dict=config,
            metric_dict=metric_dict,
            name=name,
            global_step=global_step,
        )
