# type: ignore
import nox

PYTHON_VERSIONS = ["3.6", "3.7", "3.8"]


@nox.session(venv_backend="conda")
def lint(session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/all.txt")
    session.install("-r", "requirements/dev.txt")
    session.run("flake8", "ml_logger")
    session.run("black", "--check", "ml_logger")
    session.run("mypy", "--strict", "ml_logger")


@nox.session(venv_backend="conda", python=PYTHON_VERSIONS)
def test_metrics(session) -> None:
    session.install("--upgrade", "setuptools", "pip")
    session.install("-r", "requirements/all.txt")
    session.install("-r", "requirements/dev.txt")
    session.run("pytest", "tests")
