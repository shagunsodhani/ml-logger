# type: ignore
import nox
from nox.sessions import Session


@nox.session()
def lint(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("flake8", "ml_logger")
    session.run("black", "--check", "ml_logger")


@nox.session()
def mypy(session: Session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("mypy", "--strict", "ml_logger")


@nox.session()
def test_metrics(session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/dev.txt")
    session.run("pytest", "tests")
