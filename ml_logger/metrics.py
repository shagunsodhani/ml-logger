"""Implementation of different type of metrics"""

from typing import Any, Iterable, Optional

from ml_logger.types import LogType, NumType, ValueType


class BaseMetric:
    """Base Metric class. This class is not to be used directly

    """

    def __init__(self, name: str):
        """Base Metric class

        All the metrics extend this class. It is not to be used directly

        Args:
            name (str): Name of the metric
        """
        self.name = name
        self.val: ValueType
        self.reset()

    def reset(self) -> None:
        """Reset the metric to the default value
        """
        self.val = 0

    def update(self, val: Any) -> None:
        """Update the metric using the current val

        Args:
            val (Any): Current value. This value is used to update the
                metric
        """
        pass

    def get_val(self) -> ValueType:
        """Get the current value of the metric

        """
        return self.val

    def __str__(self) -> str:
        return str(self.get_val())

    def __repr__(self) -> str:
        return f"{self.__class__} {self.__dict__}"


class CurrentMetric(BaseMetric):
    """Metric to track only the most recent value

    Args:
        BaseMetric: Base metric class
    """

    def __init__(self, name: str):
        super().__init__(name)

    def update(self, val: ValueType) -> None:
        """Update the metric using the current val

        Args:
            val (Any): Current value. The metric value is set to this value
        """
        self.val = val


class ConstantMetric(BaseMetric):
    """Metric to track one fixed value

    This is generally used for logging strings

    Args:
        BaseMetric: Base metric class
    """

    def __init__(self, name: str, val: ValueType):
        self.name = name
        self.val = val

    def reset(self) -> None:
        """This function does not do anything"""
        return None

    def update(self, val: Optional[ValueType] = None) -> None:
        """This function does not do anything

        Args:
            val (Any): This value is ignored
        """
        return None


class AverageMetric(BaseMetric):
    """Metric to track the average value

    This is generally used for logging strings

    Args:
        BaseMetric: Base metric class
    """

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
        """Update the metric using the current average value and the
            number of samples used to compute the average value

        Args:
            val (NumType): current average value
            n (int, optional): Number of samples used to compute the
                average. Defaults to 1
        """
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

    def get_val(self) -> float:
        """Get the current average value

        """
        return self.avg


class SumMetric(AverageMetric):
    """Metric to track the sum value

    Args:
        BaseMetric: Base metric class
    """

    def __init__(self, name: str):
        super().__init__(name)

    def get_val(self) -> float:
        """Get the current sum value

        """
        return self.sum


class MetricDict:
    """Class that wraps over a collection of metrics

    """

    def __init__(self, metric_list: Iterable[BaseMetric]):
        """Class that wraps over a collection of metrics

        Args:
            metric_list (Iterable[BaseMetric]): list of metrics to wrap
                over
        """
        self._metrics_dict = {metric.name: metric for metric in metric_list}

    def reset(self) -> None:
        """Reset all the metrics to default values
        """
        for key in self._metrics_dict:
            self._metrics_dict[key].reset()

    def update(self, metrics_dict: LogType) -> None:
        """Update all the metrics using the current values

        Args:
            metrics_dict (LogType): Current value of mrtrics
        """
        for key, val in metrics_dict.items():
            if key in self._metrics_dict:
                self._metrics_dict[key].update(val)

    def __str__(self) -> str:
        return "\n".join([repr(val) for key, val in self._metrics_dict.items()])

    def to_dict(self) -> LogType:
        """Method to convert the metrics into a dictionary that can be
            logged using the `LogBook`

        Returns:
            LogType: Metric data in as a dictionary
        """
        return {key: val.get_val() for key, val in self._metrics_dict.items()}
