import pathlib
from typing import Any, Dict, List, Tuple


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "#"
) -> Dict[str, Any]:
    """Flatten a given dict using the given seperator.

    Taken from https://stackoverflow.com/a/6027615/1353861

    Args:
        d (Dict[str, Any]): dictionary to flatten
        parent_key (str, optional): Keep track of the higher level key
            Defaults to "".
        sep (str, optional): string for concatenating the keys. Defaults
            to "#"

    Returns:
        Dict[str, Any]: [description]
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
    """Make dir, if not exists

    Args:
        path (str): dir to make
    """
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
