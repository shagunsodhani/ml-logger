"""Utility functions for the parser module."""
import json
from typing import Any, Dict, List, Optional, Tuple

from ml_logger.types import LogType, ValueType


def map_list_of_dicts_to_dict_of_lists(
    list_of_dicts: List[Dict[str, ValueType]]
) -> Dict[str, List[Optional[ValueType]]]:
    """Map a list of dictionary to a dictionary of lists.

    Example input: [
        {"a": 1, "b": 2},
        {"b": 3, "c": 4},]

    Example output: {
        "a": [1],
        "b": [2, 3],
        "c": [4],}

    Args:
        list_of_dicts (List[Dict[str, ValueType]]): List of dictionaries

    Returns:
        Dict[str, List[Optional[ValueType]]]: Dictionary of lists
    """
    if not list_of_dicts:
        return {}
    keys = list_of_dicts[0].keys()
    dict_of_lists = {}
    for key in keys:
        dict_of_lists[key] = [_dict.get(key, None) for _dict in list_of_dicts]
    return dict_of_lists


def flatten_log(d: LogType, parent_key: str = "", sep: str = "#") -> LogType:
    """Flatten a log using a separator.

    Taken from https://stackoverflow.com/a/6027615/1353861

    Args:
        d (LogType): [description]
        parent_key (str, optional): [description]. Defaults to "".
        sep (str, optional): [description]. Defaults to "#".

    Returns:
        LogType: [description]
    """
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_log(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def compare_logs(
    first_log: LogType, second_log: LogType, verbose: bool = False
) -> Tuple[List[str], List[str], List[str]]:
    """Compare two logs.

    Return list of keys that are either missing or have different valus
    in the two logs.

    Args:
        first_log (LogType): First Log
        second_log (LogType): Second Log
        verbose (bool): Defaults to False

    Returns:
        Tuple[List[str], List[str], List[str]]: Tuple of [
            list of keys with different values,
            list of keys with values missing in first log,
            list of keys with values missing in the second log,]
    """
    first_log = flatten_log(first_log)
    second_log = flatten_log(second_log)
    first_keys = set(first_log.keys())
    second_keys = set(second_log.keys())
    keys = first_keys.union(second_keys)
    keys_with_diff_values = []
    keys_with_missing_value_in_first_log = []
    keys_with_missing_value_in_second_log = []
    for key in keys:
        if key not in first_log:
            keys_with_missing_value_in_first_log.append(key)
            if verbose:
                print(f"first_log[{key}]: ???, second_log[{key}]: {second_log[key]}")
        elif key not in second_log:
            keys_with_missing_value_in_second_log.append(key)
            print(f"first_log[{key}]: {first_log[key]},  second_log[{key}]: ???")
        else:
            if first_log[key] != second_log[key]:
                keys_with_diff_values.append(key)
                print(
                    f"first_log[{key}]: {first_log[key]},  second_log[{key}]: {second_log[key]}"
                )
    return (
        keys_with_diff_values,
        keys_with_missing_value_in_first_log,
        keys_with_missing_value_in_second_log,
    )


def parse_json(line: str) -> Optional[LogType]:
    """Parse a line as JSON string."""
    log: Optional[LogType]
    try:
        log = json.loads(line)
    except json.JSONDecodeError:
        log = None
    return log
