from typing import Iterator

from ml_logger import metrics
from ml_logger.types import LogType


def get_first_n_natural_numbers(n: int) -> Iterator[int]:
    for current_number in range(1, n + 1):
        yield current_number


def test_current_metric() -> None:
    metric = metrics.CurrentMetric(name="test_current_metric")
    num_steps = 100
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step)
        assert metric.get_val() == current_step


def test_constant_metric() -> None:
    constant_val = 1000
    metric = metrics.ConstantMetric(name="test_constant_metric", val=constant_val)
    num_steps = 100
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step)
        assert metric.get_val() == constant_val


def test_max_metric() -> None:
    metric = metrics.MaxMetric(name="test_max_metric")
    num_steps = 100
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step)
        assert metric.get_val() == current_step


def test_min_metric() -> None:
    metric = metrics.MinMetric(name="test_min_metric")
    num_steps = 100
    for current_step in list(get_first_n_natural_numbers(num_steps))[::-1]:
        metric.update(current_step)
        assert metric.get_val() == current_step


def test_average_metric() -> None:
    metric = metrics.AverageMetric(name="test_average_metric_1")
    num_steps = 100
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step, 1)
        assert metric.get_val() == (current_step + 1) * 0.5

    metric = metrics.AverageMetric(name="test_average_metric_using_tuple")
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step, 2)
        assert metric.get_val() == (current_step + 1) * 0.5


def test_sum_metric() -> None:
    metric = metrics.SumMetric(name="test_sum_metric")
    num_steps = 100
    for current_step in get_first_n_natural_numbers(num_steps):
        metric.update(current_step)
        assert metric.get_val() == current_step * (current_step + 1) * 0.5


def test_metric_dict() -> None:
    constant_val = 1000
    metric_dict = metrics.MetricDict(
        [
            metrics.CurrentMetric(name="test_current_metric"),
            metrics.ConstantMetric(name="test_constant_metric", val=constant_val),
            metrics.MaxMetric(name="test_max_metric"),
            metrics.MinMetric(name="test_min_metric"),
            metrics.AverageMetric(name="test_average_metric"),
            metrics.AverageMetric(name="test_average_metric_using_tuple"),
            metrics.SumMetric(name="test_sum_metric"),
        ]
    )
    num_steps = 100
    metric_names = list(metric_dict.to_dict().keys())
    for current_step in get_first_n_natural_numbers(num_steps):
        current_metric_dict: LogType = {
            name: current_step
            for name in metric_names
            if name != "test_average_metric_using_tuple"
        }
        current_metric_dict["test_average_metric_using_tuple"] = (current_step, 2)
        metric_dict.update(current_metric_dict)
    actual_metric_dict = metric_dict.to_dict()
    expected_metric_dict = {
        "test_current_metric": 100,
        "test_constant_metric": 1000,
        "test_max_metric": 100,
        "test_min_metric": 1,
        "test_average_metric": 50.5,
        "test_average_metric_using_tuple": 50.5,
        "test_sum_metric": 5050.0,
    }

    assert len(actual_metric_dict) == len(expected_metric_dict)
    for key in expected_metric_dict:
        assert key in actual_metric_dict
        assert expected_metric_dict[key] == actual_metric_dict[key]
