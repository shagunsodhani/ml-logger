import json
from typing import Dict, List, Optional

from ml_logger.types import LogType, ValueType


def map_list_of_dicts_to_dict_of_lists(
    list_of_dicts: List[Dict[str, ValueType]]
) -> Dict[str, List[Optional[ValueType]]]:
    """Map a list of dictionary to a dictionary of lists

    Example input: [
        {"a": 1, "b": 2},
        {"b": 3, "c": 4},
    ]

    Example output: {
        "a": [1],
        "b": [2, 3],
        "c": [4]
    }

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


def identity_log_transformer(log: LogType) -> LogType:
    """Function to transform the log after parsing

    Args:
        log (LogType): log to transform

    Returns:
        LogType: transformed log
    """
    return log


def verbose_error_handler(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    """Function to print the error on the console, when the `log_line` is
        not a valid json string

    Args:
        log_line (str): Parsing this line triggered the error
        error (json.decoder.JSONDecodeError): The error object

    Returns:
        Optional[LogType]: None. Print the error on the console
    """
    print(f"Could not parse: {log_line} because of error: {error}")
    return None


def silent_error_handler(
    log_line: str, error: json.decoder.JSONDecodeError
) -> Optional[LogType]:
    """Function to silently ignore the error, when the `log_line` is
        not a valid json string

    Args:
        log_line (str): Parsing this line triggered the error
        error (json.decoder.JSONDecodeError): The error object

    Returns:
        Optional[LogType]: None. Nothing is done
    """
    return None
