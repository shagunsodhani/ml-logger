import codecs
import os.path

import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    # code taken from https://packaging.python.org/guides/single-sourcing-package-version/
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def parse_dependency(filepath):
    return [
        dependency
        for dependency in open(filepath).read().splitlines()
        if "==" in dependency
    ]


base_requirements = parse_dependency("requirements/filesystem.txt")
all_requirements = base_requirements + parse_dependency("requirements/all.txt")
dev_requirements = all_requirements + parse_dependency("requirements/dev.txt")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mllogger",
    version=get_version("ml_logger/__init__.py"),
    author="Shagun Sodhani",
    author_email="sshagunsodhani@gmail.com",
    description="Logging Utility for ML Experiments",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # Install the basic setup (without wandb, tensorboardX and mlflow) with
    install_requires=base_requirements,
    url="https://github.com/shagunsodhani/ml-logger",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "docs", "docsrc"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    extras_require={
        # Install development dependencies with
        # pip install -e .[dev]
        "dev": dev_requirements,
        # Install the complete setup (wandb, mlflow and tensorboardX)
        # pip install .[all]
        "all": all_requirements,
    },
)
