from copy import deepcopy

import pytest

from ml_logger.parser.experiment import Parser
from tests.utils import get_logs_and_types_for_parser, make_logbook

logbook_keys = ["logbook_id", "logbook_timestamp", "logbook_type"]


def assert_logbook_keys_exist(log, logbook_type):
    assert isinstance(log, dict)
    for key in logbook_keys:
        assert key in log
    assert log["logbook_type"] == logbook_type


def group_logs_by_type(logs):
    groups = {}
    for log, log_type in logs:
        if log_type not in groups:
            groups[log_type] = []
        groups[log_type].append(log)
    return groups


def prep_log_before_comparing(log):
    log_to_return = deepcopy(log)
    for key in logbook_keys:
        log_to_return.pop(key)
    return log_to_return


@pytest.mark.parametrize("logs", get_logs_and_types_for_parser())
def test_parser(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    for log, log_type in logs:
        logbook.write(log, log_type)
    parser = Parser()
    experiment = parser.parse(tmp_path)
    grouped_logs = group_logs_by_type(logs)
    for key in ["message", "metadata"]:
        compare_components(experiment.info[key], grouped_logs[key], key)
    key = "config"
    compare_components(experiment.configs, grouped_logs[key], key)
    breakpoint()


def compare_components(exp_component, log_group, key):
    assert len(exp_component) == len(log_group)
    for exp_item, log_item in zip(exp_component, log_group):
        assert_logbook_keys_exist(exp_item, key)
        assert prep_log_before_comparing(exp_item) == log_item
