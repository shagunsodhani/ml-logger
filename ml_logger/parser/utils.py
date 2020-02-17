from typing import Dict, List, Optional

from ml_logger.types import ValueType


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
