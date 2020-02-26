"""Logger class that writes to wandb"""

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType
from tensorboardX import SummaryWriter


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

        global_step = None
        if "global_step" in log:
            global_step = log.pop("global_step")
        walltime = None
        if "walltime" in log:
            walltime = log.pop("walltime")

        main_tag = None
        if "tag" in log:
            main_tag = log.pop("tag")
        elif "main_tag" in log:
            main_tag = log.pop("main_tag")

        if logbook_type == "metric":
            self.summary_writer.add_scalars(
                main_tag=main_tag,
                tag_scalar_dict=log,
                global_step=global_step,
                walltime=walltime,
            )
        else:
            pass
            # Only metric logs can be written to tensorboardX
