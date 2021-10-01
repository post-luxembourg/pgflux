from os.path import join

from setuptools import find_packages, setup

setup(
    name="pgflux",
    version="0.0.0",
    description="Script for monitoring PostgreSQL databases with InfluxDB",
    long_description=open("README.rst").read(),
    author="Michel Albert",
    author_email="michel.albert@post.lu",
    license="MIT",
    include_package_data=True,
    install_requires=[
        "importlib_metadata; python_version < '3.8'",
        "psycopg2-binary",
    ],
    extras_require={
        "dev": [
            "recommonmark",
            "sphinx",
            "sphinx-rtd-theme",
            "mypy",
            "pylint",
            "python-dotenv",
        ],
        "test": [
            "pytest",
            "pytest-cache",
            "pytest-coverage",
        ],
    },
    packages=find_packages(exclude=["tests.*", "tests"]),
)
