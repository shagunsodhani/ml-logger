import numpy as np

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
    log1 = [
        {
            "num_layers": 2,
            "lr": 0.01,
            "alpha": np.float64(0.2),
            "beta": np.float32(0.1),
            "gamma": np.int64(1),
            "delta": np.int32(10),
        },
        {"dataset": "mnist", "optim": "adam"},
    ]
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
    log4 = [
        ["num_layers=2"],
        ["lr=0.01"],
        [
            f"alpha:{np.float64(0.2)}, beta:{np.float32(0.1)}, gamma:{np.int64(1)}, delta: {np.int32(10)}"
        ],
    ]
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
    log5 = [
        {
            "unnested_metric": 1,
            "nested_metric": {
                "metric1": 3,
                "metric2": 0.001,
                "alpha": np.float64(0.2),
                "beta": np.float32(0.1),
                "gamma": np.int64(1),
                "delta": np.int32(10),
            },
        }
    ]
    return [log1, log2, log3, log4, log5]


def _get_invalid_metric_logs():
    log1 = [["acc=10.1", "mode=train"]]
    log2 = [None]
    log3 = [[]]
    return [log1, log2, log3]


def get_logs(log_type: str = "config", valid: bool = True):
    if log_type == "config" or log_type == "metadata":
        # both config and metadata have the same type.
        if valid:
            return _get_valid_config_logs()
        return _get_invalid_config_logs()
    elif log_type == "message":
        if valid:
            return _get_valid_message_logs()
        return _get_invalid_message_logs()
    elif log_type == "metric":
        if valid:
            return _get_valid_metric_logs()
        return _get_invalid_metric_logs()


def get_logs_and_types(valid: bool = True):
    log_types = ["config", "metadata", "metric"]
    if not valid:
        log_types.append("message")
        # generally messages can not be directly written using `logbook.write`
    for _type in log_types:
        for log in get_logs(log_type=_type, valid=valid):
            yield (log, _type)


def get_logs_and_types_for_parser():
    logs_and_types = [
        ({"num_layers": 2, "lr": 0.01}, "config"),
        ({"dataset": "mnist", "optim": "adam"}, "config"),
        (
            {
                "alpha": np.float64(0.2),
                "beta": np.float32(0.1),
                "gamma": np.int64(1),
                "delta": np.int32(10),
            },
            "config",
        ),
        ({"message": "Starting training."}, "message"),
        ({"best_acc_so_far": 0.0, "best_lr": 0.01}, "metadata"),
        ({"acc": 20.2, "loss": 0.01, "mode": "train", "epoch": 1}, "metric"),
        ({"acc": 40.4, "loss": 0.001, "mode": "train", "epoch": 2}, "metric"),
        (
            {"acc@1": 21.3, "acc@5": 50.2, "loss": 0.001, "mode": "eval", "epoch": 2},
            "metric",
        ),
        ({"best_acc_so_far": 21.3, "best_lr": 0.01}, "metadata"),
        ({"message": "Ending training."}, "message"),
    ]
    return [logs_and_types]
