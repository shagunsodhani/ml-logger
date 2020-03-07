"""Abstract logger class"""
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from ml_logger.types import ConfigType, KeyMapType, LogType


class Logger(metaclass=ABCMeta):
    """Abstract Logger Class
    """

    @abstractmethod
    def __init__(self, config: ConfigType):
        """Initialise the Logger

        Args:
            config (ConfigType): config to initialise the logger
        """
        self.keys_to_retain: Optional[List[str]] = None
        self.keys_to_skip: Optional[List[str]] = None
        self.keys_to_check: Optional[List[str]] = None
        self.key_map: Optional[KeyMapType] = config.pop("logbook_key_map")
        self.key_prefix: Optional[str] = config.pop("logbook_key_prefix")

    @abstractmethod
    def write_log(self, log: LogType) -> None:
        """Interface to write the log

        Args:
            log (LogType): Log to write
        """
        pass

    def _prepare_log_to_write(self, log: LogType) -> LogType:
        """Remove certain keys before writing the log.

        LogBook adds some keys to track metadata. These keys are filtered
        for some loggers (like wandb).

        `self.keys_to_retain` informs what keys are to be retained. All
        keys are retained if `self.keys_to_retain` is None.

        `self.keys_to_skip` informs what keys are to be skipped. No key
        is skipped if `self.keys_to_skip` is None.

        Args:
            log (LogType): Log to write

        Returns:
            LogType: Log with certain keys removed
        """
        processed_log: LogType = {}

        if self.keys_to_retain is None:
            # Retain all the keys, other than the ones to skip
            processed_log = log
        else:
            # Retain only the keys that need to be retained
            for key in self.keys_to_retain:
                processed_log[key] = log[key]

        if self.keys_to_skip is not None:
            for key in self.keys_to_skip:
                if key in processed_log:
                    processed_log.pop(key)
        return processed_log

    def _prepare_metric_log_to_write(self, log: LogType) -> LogType:
        """Map some keys to another keys, remove some keys before writing
        the log.

        Some loggers require specific keys to be present. User can specify
        those keys via a different name and should be mapped to the required
        name before passing to the logger.

        LogBook adds some keys to track metadata. These keys are filtered
        for some loggers (like wandb).

        `self.keys_to_retain` informs what keys are to be retained. All
        keys are retained if `self.keys_to_retain` is None.

        `self.keys_to_skip` informs what keys are to be skipped. No key
        is skipped if `self.keys_to_skip` is None.

        Args:
            log (LogType): Log to write

        Returns:
            LogType: Log with certain keys removed
        """

        if self.key_map is not None:
            for key, mapped_key in self.key_map.items():
                log[mapped_key] = log.pop(key)
        return self._prepare_log_to_write(log=log)
