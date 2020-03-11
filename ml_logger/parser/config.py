"""Implementation of Parser to parse the logs"""

import glob
import json
from typing import Callable, Optional

import tinydb

from ml_logger.parser import parser as base_parser
from ml_logger.parser import utils as parser_utils
from ml_logger.types import ConfigType, LogType


class Parser(base_parser.Parser):
    """Class to parse the config in the log files
    """

    def __init__(
        self,
        log_transformer: Callable[
            [LogType], LogType
        ] = parser_utils.identity_log_transformer,
        error_handler: Callable[
            [str, json.decoder.JSONDecodeError], Optional[LogType]
        ] = parser_utils.silent_error_handler,
    ):
        """Class to parse the log files

        Args:
            log_transformer (Callable[[LogType], LogType], optional):
                Function to transform the logs after reading them from the
                filesystem. Defaults to parser_utils.identity_log_transformer.
            error_handler (Callable[[str, json.decoder.JSONDecodeError],
                Optional[LogType]], optional): Function to handle the
                error when the parser reads an invalid json string.
                Defaults to parser_utils.silent_error_handler.
        """

        super().__init__(
            log_transformer=log_transformer, error_handler=error_handler,
        )
        self.log_type = "config"

    def get_config(self, file_path: str) -> Optional[ConfigType]:
        """Method to get the config from the log file.

        The different between `get_config` and `get_logs` function is that
        `get_logs` returns an iterator over all the configs that are found
        in a log file while `get_config` only returns the last config. The same
        config file may be written multiple times in a log file. Hence
        `get_config` should be the default method for getting the config

        Args:
            file_path (str): Log file to read from

        Returns:
            ConfigType: Config object
        """

        configs = list(self.get_logs(file_path=file_path))
        if configs:
            return configs[-1]
        return None

    def load_configs_from_path(
        self, path_pattern: str, path_to_save: str = "config.json"
    ) -> tinydb.TinyDB:
        """Method to glob the given path pattern and load config from
        all the matching paths

        Args:
            path_pattern (str): path pattern to glob
            path_to_save (str): filesystem path where the loaded configs
                are saved. Defaults to config.json.

        Returns:
            tinydb.TinyDB: TinyDB database instance over the collection of configs
        """
        db = tinydb.TinyDB(path_to_save)
        paths = glob.glob(path_pattern)
        for file_path in paths:
            config = self.get_config(file_path=file_path)
            if config is not None:
                config["file_path"] = file_path
                db.insert(config)
        return db
