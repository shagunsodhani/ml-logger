from typing import Any, Dict, Union

ValueType = Union[str, int, float]
NumType = Union[int, float]
ConfigType = Dict[str, Any]
LogType = Dict[str, ValueType]
MetricType = LogType
ModelType = Any
RemoteMetricType = Dict[str, Union[MetricType, ValueType]]
# Type of the metric that is written to remote
