from typing import List

import ray
from omegaconf import OmegaConf
from pymongo import MongoClient

from ml_logger.parser.experiment.store.record import (
    Record,
    make_record,
    ray_make_record,
)
from ml_logger.types import ConfigType


class MongoStore:
    def __init__(
        self, config: ConfigType,
    ):
        """Class to interface with the mongodb store
        Args:
            config (ConfigType): Config to connect with the mongo store.
        """
        self._client = MongoClient(host=config["host"], port=config["port"])
        db = config["db"]
        collection_name = config["collection_name"]
        self.collection = self._client[db][collection_name]

    def ray_get_records(self) -> List[Record]:
        futures = [ray_make_record.remote(record) for record in self.collection.find()]
        records = ray.get(futures)
        assert isinstance(records, List)
        return records

    def get_records(self) -> List[Record]:
        return [make_record(record) for record in self.collection.find()]

    def delete_records(self, records: List[Record]) -> None:
        for record in records:
            print(self.collection.delete_one({"_id": record.id}).deleted_count)

    def mark_records_as_analyzed(self, records: List[Record]) -> None:
        for record in records:
            OmegaConf.set_struct(record.config, False)
            OmegaConf.set_readonly(record.config, False)
            record.config.status = "ANALYZED"
            print(
                self.collection.replace_one(
                    {"_id": record.id}, OmegaConf.to_container(record.config)
                ).raw_result
            )

    def get_unanalyzed_records(self) -> List[Record]:
        return [
            record
            for record in self.get_records()
            if record.config.status != "ANALYZED"
        ]
