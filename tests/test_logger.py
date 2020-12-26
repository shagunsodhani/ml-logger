import pytest

from tests.utils import get_logs, get_logs_and_types, make_logbook


@pytest.mark.parametrize("logs", get_logs(log_type="config", valid=True))
def test_write_valid_config_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    for log in logs:
        logbook.write_config(log)


@pytest.mark.parametrize("logs", get_logs(log_type="config", valid=False))
def test_write_invalid_config_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    with pytest.raises(TypeError):
        for log in logs:
            logbook.write_config(log)


@pytest.mark.parametrize("logs", get_logs(log_type="message", valid=True))
def test_write_valid_message_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    for log in logs:
        logbook.write_message(log)


@pytest.mark.parametrize("logs", get_logs(log_type="message", valid=False))
def test_write_invalid_message_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    with pytest.raises(TypeError):
        for log in logs:
            logbook.write_message(log)


@pytest.mark.parametrize("logs", get_logs(log_type="metadata", valid=True))
def test_write_valid_metadata_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    for log in logs:
        logbook.write_metadata(log)


@pytest.mark.parametrize("logs", get_logs(log_type="metadata", valid=False))
def test_write_invalid_metadata_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    with pytest.raises(TypeError):
        for log in logs:
            logbook.write_metadata(log)


@pytest.mark.parametrize("logs", get_logs(log_type="metric", valid=True))
def test_write_valid_metric_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    for log in logs:
        logbook.write_metric(log)


@pytest.mark.parametrize("logs", get_logs(log_type="metric", valid=False))
def test_write_invalid_metric_logs(tmp_path, logs):
    logbook = make_logbook(tmp_path)
    with pytest.raises(TypeError):
        for log in logs:
            logbook.write_metric(log)


@pytest.mark.parametrize("logs, log_type", get_logs_and_types(valid=True))
def test_logger_with_valid_logs(tmp_path, logs, log_type):
    logbook = make_logbook(tmp_path)
    for log in logs:
        logbook.write(log, log_type)


@pytest.mark.parametrize("logs, log_type", get_logs_and_types(valid=False))
def test_logger_with_invalid_logs(tmp_path, logs, log_type):
    logbook = make_logbook(tmp_path)
    with pytest.raises(TypeError):
        for log in logs:
            logbook.write(log, log_type)
