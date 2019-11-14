import collections
import pathlib
from typing import Dict


def flatten_dict(d: Dict, parent_key: str = "", sep: str = "#") -> Dict:
    """Method to flatten a given dict using the given seperator.
    Taken from https://stackoverflow.com/a/6027615/1353861
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def make_dir(path: string) -> None:
    """Make dir, if not exists"""
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
