"""List of different type of metrics"""

from typing import Any, Iterable, Optional

from ml_logger.types import LogType, NumType, ValueType


class BaseMetric:
    """Base Metric class. This class is not to be used directly"""

    def __init__(self, name: str):
        self.name = name
        self.val: ValueType
        self.reset()

    def reset(self) -> None:
        self.val = 0

    def update(self, val: Any) -> None:
        pass

    def get_val(self) -> ValueType:
        return self.val

    def __str__(self) -> str:
        return str(self.get_val())

    def __repr__(self) -> str:
        return f"{self.__class__} {self.__dict__}"


class CurrentMetric(BaseMetric):
    """Metric to track only the most recent value"""

    def __init__(self, name: str):
        super().__init__(name)

    def update(self, val: ValueType) -> None:
        self.val = val


class ConstantMetric(BaseMetric):
    """Metric to track one fixed value. This is generally used for logging strings"""

    def __init__(self, name: str, val: ValueType):
        self.name = name
        self.val = val

    def reset(self) -> None:
        return None

    def update(self, val: Optional[ValueType] = None) -> None:
        return None


class AverageMetric(BaseMetric):
    """Metric to track the average value"""

    def __init__(self, name: str):
        self.name = name
        self.val: float
        self.avg: float
        self.sum: float
        self.count: float
        self.reset()

    def reset(self) -> None:
        self.val = 0.0
        self.avg = 0.0
        self.sum = 0.0
        self.count = 0.0

    def update(self, val: NumType, n: int = 1) -> None:
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

    def get_val(self) -> float:
        return self.avg


class SumMetric(AverageMetric):
    """Metric to track the sum value"""

    def __init__(self, name: str):
        super().__init__(name)

    def get_val(self) -> float:
        return self.sum


class MetricDict:
    """Dict that wraps over a collection of metrics"""

    def __init__(self, metric_list: Iterable[BaseMetric]):
        self._metrics_dict = {metric.name: metric for metric in metric_list}

    def reset(self) -> None:
        for key in self._metrics_dict:
            self._metrics_dict[key].reset()

    def update(self, metrics_dict: LogType) -> None:
        for key, val in metrics_dict.items():
            if key in self._metrics_dict:
                self._metrics_dict[key].update(val)

    def __str__(self) -> str:
        return "\n".join([repr(val) for key, val in self._metrics_dict.items()])

    def to_dict(self) -> LogType:
        """Method to get a dict that can be written to the logbook"""
        return {key: val.get_val() for key, val in self._metrics_dict.items()}
