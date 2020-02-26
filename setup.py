import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ml_logger",
    version="0.3rc1",
    author="Shagun Sodhani",
    author_email="sshagunsodhani@gmail.com",
    description="Logging Utility for ML Experiments",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=open("requirements/all.txt").read().splitlines(),
    url="https://github.com/shagunsodhani/ml-logger",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "docs"]
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
        "dev": open("requirements/dev.txt").read().splitlines(),
        # Install the basic setup (without wandb and tensorboardX) with
        # pip install .[base]
        "base": open("requirements/base.txt").read().splitlines(),
    },
)
