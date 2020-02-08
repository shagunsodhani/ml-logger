import collections
import pathlib
from typing import Any, Dict, List, Tuple


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "#"
) -> Dict[str, Any]:
    """Method to flatten a given dict using the given seperator.
    Taken from https://stackoverflow.com/a/6027615/1353861
    """
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def make_dir(path: str) -> None:
    """Make dir, if not exists"""
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
