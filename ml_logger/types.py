from typing import Any, Callable, Dict, Union

NumType = Union[int, float]
ValueType = Union[str, int, float]
LogType = Dict[str, Any]
ConfigType = LogType
MetricType = Dict[str, ValueType]
ModelType = Any
ComparisonOpType = Callable[[ValueType, ValueType], bool]
