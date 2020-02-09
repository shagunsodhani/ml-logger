[![CircleCI](https://circleci.com/gh/shagunsodhani/ml-logger.svg?style=svg)](https://circleci.com/gh/shagunsodhani/ml-logger) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

# ml-logger
Logging utility for ML experiments

### Setup

* `pip install .`

### Documentation

[https://shagunsodhani.github.io/ml-logger](https://shagunsodhani.github.io/ml-logger/)

### Dev Setup

* `pip install -e .[dev] -e .`
* Install pre-commit hooks `pre-commit install`
* The code is linted using:
    * `black`
    * `flake8`
    * `mypy`
* CI currently only checks for linting. 
* Lint tests can be run locally using `nox -s lint`

### Acknowledgements

* Config for `circleci`, `pre-commit`, `mypy` etc are borrowed/modified from [Hydra](https://github.com/facebookresearch/hydra)