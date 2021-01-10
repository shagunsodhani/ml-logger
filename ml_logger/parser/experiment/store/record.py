"""Wrappper over mongodb records."""
from dataclasses import dataclass

import ray
from bson.objectid import ObjectId
from omegaconf import DictConfig, OmegaConf

from ml_logger.types import ConfigType


@dataclass
class Record:
    id: ObjectId
    config: DictConfig


def make_record(config: ConfigType) -> Record:
    _id = config.pop("_id")
    record_config = OmegaConf.create(config)
    OmegaConf.set_struct(record_config, True)
    OmegaConf.set_readonly(record_config, True)
    return Record(id=_id, config=record_config)


@ray.remote  # type: ignore
# Ignoring error: Untyped decorator makes function "ray_make_record" untyped
def ray_make_record(config: ConfigType) -> Record:
    return make_record(config)
