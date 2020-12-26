# type: ignore
import os

import nox
from nox.sessions import Session

DEFAULT_PYTHON_VERSIONS = ["3.6", "3.7", "3.8", "3.9"]

PYTHON_VERSIONS = os.environ.get(
    "NOX_PYTHON_VERSIONS", ",".join(DEFAULT_PYTHON_VERSIONS)
).split(",")

paths_to_check = ["ml_logger", "noxfile.py"]


@nox.session(python=PYTHON_VERSIONS)
def lint(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("flake8", "ml_logger")
    for _path in paths_to_check:
        session.run("black", "--check", _path)


@nox.session(python=PYTHON_VERSIONS)
def mypy(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    for _path in paths_to_check:
        session.run("mypy", "--strict", _path)


@nox.session(python=PYTHON_VERSIONS)
def test_metrics(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("pytest", "tests")
