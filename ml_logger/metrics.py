"""Implementation of different type of metrics"""

import operator
from typing import Any, Iterable, Optional, Union

from ml_logger.types import ComparisonOpType, LogType, NumType, ValueType


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


class ComparisonMetric(BaseMetric):
    """Metric to track the min/max value

    This is generally used for logging best accuracy, least loss, etc.

    Args:
        BaseMetric: Base metric class
    """

    def __init__(
        self, name: str, default_val: ValueType, comparison_op: ComparisonOpType
    ):
        """Metric to track the min/max value

        This is generally used for logging best accuracy, least loss, etc.

        Args:
            name (str): Name of the metric
            default_val (ValueType): Default value to initialise the metric
            comparison_op (ComparisonOpType): Operator to compare the current
                value with the incoming value.
                If comparison_op(current_val, new_val) is true, we update
                the current value.
        """
        self.name = name
        self._default_val = default_val
        self.comparison_op = comparison_op
        self.val = default_val

    def reset(self) -> None:
        """Reset the metric to the default value"""
        self.val = self._default_val

    def update(self, val: ValueType) -> None:
        """Use the comparison operator to decide which value to keep

        If the output of self.comparison_op(val, self)

        Args:
            val (ValueType): Value to compare the current value with.
                If comparison_op(current_val, new_val) is true, we update
                the current value.
        """
        if self.comparison_op(self.val, val):
            self.val = val


class MaxMetric(ComparisonMetric):
    """Metric to track the max value

    This is generally used for logging best accuracy, etc.

    Args:
        ComparisonMetric: Comparison metric class
    """

    def __init__(self, name: str):
        """Metric to track the max value

        This is generally used for logging best accuracy, etc.

        Args:
            name (str): Name of the metric
        """
        super().__init__(
            name=name, default_val=float("-inf"), comparison_op=operator.lt
        )


class MinMetric(ComparisonMetric):
    """Metric to track the min value

    This is generally used for logging least loss, etc.

    Args:
        ComparisonMetric: Comparison metric class
    """

    def __init__(self, name: str):
        """Metric to track the min value

        This is generally used for logging least loss, etc.

        Args:
            name (str): Name of the metric
        """
        super().__init__(name=name, default_val=float("inf"), comparison_op=operator.gt)


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

    def update(self, metrics_dict: Union[LogType, "MetricDict"]) -> None:
        """Update all the metrics using the current values

        Args:
            metrics_dict (Union[LogType, MetricDict]): Current value of metrics
        """
        if isinstance(metrics_dict, MetricDict):
            metrics_dict = metrics_dict.to_dict()
        for key, val in metrics_dict.items():
            if key in self._metrics_dict:
                if isinstance(val, (str, float, int)):
                    self._metrics_dict[key].update(val)
                else:
                    self._metrics_dict[key].update(*val)

    def __str__(self) -> str:
        return "\n".join([repr(val) for key, val in self._metrics_dict.items()])

    def to_dict(self) -> LogType:
        """Method to convert the metrics into a dictionary that can be
            logged using the `LogBook`

        Returns:
            LogType: Metric data in as a dictionary
        """
        return {key: val.get_val() for key, val in self._metrics_dict.items()}
