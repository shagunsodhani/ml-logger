from ml_logger import logbook as ml_logbook
from ml_logger.types import ConfigType


def make_logbook_config(logger_dir: str) -> ConfigType:
    return ml_logbook.make_config(
        logger_dir=logger_dir,
        wandb_config=None,
        tensorboard_config=None,
        mlflow_config=None,
    )


def make_logbook(logger_dir: str) -> ml_logbook.LogBook:
    logbook = ml_logbook.LogBook(config=make_logbook_config(logger_dir))
    return logbook


def _get_valid_config_logs():
    log1 = [{"num_layers": 2, "lr": 0.01}, {"dataset": "mnist", "optim": "adam"}]
    log2 = [{"num_layers": 2, "lr": 0.01}, {"num_layers": 3, "lr": 0.001, "none": None}]
    log3 = [{}]
    log4 = []
    log5 = [{"num_layers": 2, "subconfig": {"num_layers": 3, "lr": 0.001}}]
    return [log1, log2, log3, log4, log5]


def _get_invalid_config_logs():
    log1 = [["num_layers=2", "lr=0.01"]]
    log2 = [None]
    log3 = [[]]
    return [log1, log2, log3]


def _get_valid_message_logs():
    log1 = ["This is a message", "This is another message"]
    log2 = [""]
    log3 = []
    log4 = [["num_layers=2"], ["lr=0.01"]]
    log5 = [{}, [], None]
    log6 = [{"num_layers": 2, "lr": 0.01}, {"dataset": "mnist", "optim": "adam"}]
    log7 = [
        {
            "first_message": "a",
            "nested_message": {
                "lr": 0.01,
                "datasets": ["mnist", "cifar"],
                "optim": "adam",
            },
        }
    ]
    return [log1, log2, log3, log4, log5, log6, log7]


def _get_invalid_message_logs():
    return [None]


def _get_valid_metric_logs():
    log1 = [{"acc": 20.2, "loss": 0.01}, {"acc@1": 10.1, "mode": "train"}]
    log2 = [{"acc": 20.2, "loss": 0.01, "acc@1": 10.1, "mode": "train", "none": None}]
    log3 = [{}]
    log4 = []
    log5 = [{"unnested_metric": 1, "nested_metric": {"metric1": 3, "metric2": 0.001}}]
    return [log1, log2, log3, log4, log5]


def _get_invalid_metric_logs():
    log1 = [["acc=10.1", "mode=train"]]
    log2 = [None]
    log3 = [[]]
    return [log1, log2, log3]


def get_logs(log_type: bool = "config", valid: bool = True):
    if log_type == "config" or log_type == "metadata":
        # both config and metadata have the same type.
        if valid:
            return _get_valid_config_logs()
        else:
            return _get_invalid_config_logs()
    elif log_type == "message":
        if valid:
            return _get_valid_message_logs()
        else:
            return _get_invalid_message_logs()
    elif log_type == "metric":
        if valid:
            return _get_valid_metric_logs()
        else:
            return _get_invalid_metric_logs()


# def get_logs_list():
#     return get_config_logs()
#     logs_list = []
# log = {"epoch": 1, "loss": 0.1, "accuracy": 0.2}
# logs = [log]
# return [logs]
