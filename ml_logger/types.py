"""Types used in the package."""
from typing import Any, Callable, Dict, Optional, Union

NumType = Union[int, float]
ValueType = Union[str, int, float]
LogType = Dict[str, Any]
ParseLineFunctionType = Callable[[str], Optional[LogType]]
ConfigType = LogType
MetricType = LogType
ModelType = Any
ComparisonOpType = Callable[[ValueType, ValueType], bool]
KeyMapType = Dict[str, str]
