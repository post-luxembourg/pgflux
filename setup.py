from setuptools import find_packages, setup

setup(
    name="pgflux",
    version="1.0.2",
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
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Monitoring",
        "Typing :: Typed",
    ],
    project_urls={
        "Source": "https://github.com/post-luxembourg/pgflux",
        "Tracker": "https://github.com/post-luxembourg/pgflux/issues",
        "Documentation": "https://post-luxembourg.github.io/pgflux/",
    },
    keywords=["influxdb", "postgresql"],
)
