from setuptools import find_packages, setup

setup(
    name="pgflux",
    version="1.0.0.post3",
    description="Script for monitoring PostgreSQL databases with InfluxDB",
    long_description=open("README.rst").read(),
    author="Michel Albert",
    author_email="michel.albert@post.lu",
    license="MIT",
    include_package_data=True,
    install_requires=[
        "importlib_metadata; python_version < '3.8'",
        "psycopg2-binary",
        "python-dotenv",
    ],
    entry_points={"console_scripts": ["pgflux=pgflux.cli:main"]},
    extras_require={
        "dev": [
            "black",
            "pylint",
            "sphinx",
            "sphinx-rtd-theme",
        ],
        "test": [
            "pytest",
            "pytest-cache",
            "pytest-coverage",
        ],
    },
    packages=find_packages(exclude=["tests.*", "tests"]),
)
