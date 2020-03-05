[![CircleCI](https://circleci.com/gh/shagunsodhani/ml-logger.svg?style=svg)](https://circleci.com/gh/shagunsodhani/ml-logger) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# ml-logger
Logging utility for ML experiments

### Installation

* `git clone git@github.com:shagunsodhani/ml-logger.git`
* `cd ml-logger`
* `pip install .`

Alternatively, `pip install git://git@github.com/shagunsodhani/ml-logger.git@master#egg=ml_logger`

If you want to use tensorboardX or Wandb logger, use `pip install .[all]` or `pip install git://git@github.com/shagunsodhani/ml-logger.git@master#egg=ml_logger[all]`

### Use

* Make a `logbook_config`:

    ```
    from ml_logger import logbook as ml_logbook
    logbook_config = ml_logbook.make_config(
        logger_file_path = <path to write logs>,
        wandb_config = <wandb config or None>,
        tensorboard_config = <tensorboard config or None>)
    ```

    The API for `make_config` can be accessed [here](https://shagunsodhani.com/ml-logger/logbook.html#ml_logger.logbook.make_config).

* Make a `LogBook` instance:

    ```
    logbook = ml_logbook.LogBook(config = logbook_config)
    ```

* Use the `logbook` instance:

    ```
    log = {
        "epoch": 1,
        "loss": 0.1,
        "accuracy": 0.2
    }
    logbook.write_log(log)
    ```
    The API for `write_log` can be accessed [here](https://shagunsodhani.com/ml-logger/logbook.html#ml_logger.logbook.LogBook.write_metric_log).

    If you are writing to wandb, the log must have a key called `step`.

    If you are writing to tensorboard, the log must have a key called `main_tag` or `tag` which acts as the data Identifier (described [here](https://tensorboardx.readthedocs.io/en/latest/tensorboard.html#tensorboardX.SummaryWriter.add_scalars))


### Documentation

[https://shagunsodhani.github.io/ml-logger](https://shagunsodhani.github.io/ml-logger/)

### Dev Setup

* `pip install -e .[dev]`
* Install pre-commit hooks `pre-commit install`
* The code is linted using:
    * `black`
    * `flake8`
    * `mypy`
* CI currently only checks for linting. 
* Lint tests can be run locally using `nox -s lint`

### Acknowledgements

* Config for `circleci`, `pre-commit`, `mypy` etc are borrowed/modified from [Hydra](https://github.com/facebookresearch/hydra)
