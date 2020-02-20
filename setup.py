import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="ml_logger",
    version="0.2",
    author="Shagun Sodhani",
    author_email="sshagunsodhani@gmail.com",
    description="Logging Utility for ML Experiments",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["pandas==0.25.3", "tinydb==3.15.2"],
    url="https://github.com/shagunsodhani/ml-logger",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    # Install development dependencies with
    # pip install -e .[dev]
    extras_require={"dev": requirements},
)
