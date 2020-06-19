# type: ignore
import nox
from nox.sessions import Session

paths_to_check = ["ml_logger", "noxfile.py"]


@nox.session()
def lint(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("flake8", "ml_logger")
    for _path in paths_to_check:
        session.run("black", "--check", _path)


@nox.session()
def mypy(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    for _path in paths_to_check:
        session.run("mypy", "--strict", _path)


@nox.session()
def test_metrics(session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("pytest", "tests")
