"""Functions to interface with the mongodb."""


from pymongo import MongoClient

from ml_logger.logger.base import Logger as BaseLogger
from ml_logger.types import ConfigType, LogType


class Logger(BaseLogger):
    """Logger class that writes to the mongodb."""

    def __init__(self, config: ConfigType):
        """Initialise the Mongodb Logger.

        Args:
            config (ConfigType): config to initialise the mongodb logger.
                It must have four keys: host, port, db and collection.
                "logger_file_path" is the path to the file where the logs
                will be written. "logger_name" is the name of the logger instance
        """
        super().__init__(config=config)
        keys_to_check = [
            "host",
            "port",
            "db",
            "collection",
        ]
        if not all(key in config for key in keys_to_check):
            key_string = ", ".join(keys_to_check)
            raise KeyError(
                f"One or more of the following keys missing in the config: {key_string}"
            )

        self.logger_types = {"config", "message", "metadata"}
        self.client = MongoClient(config["host"], config["port"])
        self.collection = self.client[config["db"]][config["collection"]]

    def write(self, log: LogType) -> None:
        """Write the log to the filesystem.

        Args:
            log (LogType): Log to write
        """
        if log["logbook_type"] in self.logger_types:
            self.collection.insert_one(log)
