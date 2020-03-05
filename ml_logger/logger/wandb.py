"""Logger class that writes to wandb"""

import wandb

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType


class Logger(BaseLogger):
    """Logger class that writes to wandb
    """

    def __init__(self, config: ConfigType):
        """Initialise the Wandb Logger

        Args:
            config (ConfigType): config to initialise the wandb logger.
                The config can have any parameters that wandb.init() method
                accepts (https://docs.wandb.com/library/init). Note that
                the config is passed as keyword arguments to the wandb.init()
                method. This provides a lot of flexibility to the users to
                configure wandb. This also means that config should not
                have any parameters that wandb.init() would not accept.
        """
        super().__init__(config=config)
        self.keys_to_skip = ["logbook_id", "logbook_type", "logbook_timestamp"]
        self.keys_to_check = ["step"]
        self.run = wandb.init(**config)

    def write_log(self, log: LogType) -> None:
        """Write the log to wandb

        Args:
            log (LogType): Log to write
        """
        logbook_type = log["logbook_type"]
        log = self._prepare_log_to_write(log=log)
        if logbook_type == "config":
            self.write_config(config=log)
        elif logbook_type == "metric":
            assert self.keys_to_check is not None
            for key in self.keys_to_check:
                assert key in log
            step = log.pop("step")
            wandb.log(log, step)
        else:
            pass
            # Message can not be written to wandb

    def write_config(self, config: ConfigType) -> None:
        """Write the config to wandb

        Args:
            config (ConfigType): Config to write
        """
        wandb.config.update(config)
