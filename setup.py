#!/usr/bin/env python
import re
import os

from setuptools import setup

with open("README.rst") as fp:
    long_desc = fp.read()

with open("flask_storm/__init__.py") as fp:
    version = re.search('__version__\s+=\s+"([^"]+)', fp.read()).group(1)

if __name__ == "__main__":
    setup(
        name="Flask-Storm",
        version=version,
        description="Storm integration for Flask.",
        long_description=long_desc,
        license="MIT",
        author="Andreas Runfalk",
        author_email="andreas@runfalk.se",
        url="https://www.github.com/runfalk/flask_storm",
        py_modules=["flask_storm"],
        install_requires=[
            "Flask",
            "storm"
        ],
        extras_require={
            "dev": [
                "mock",
                "pytest",
                "pytest-cov",
                "sphinx",
            ],
            "fancy": [
                "sqlparse",
            ],
        },
        classifiers=(
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Topic :: Utilities",
        ),
        zip_safe=False,
        test_suite="test_flask_storm.suite"
    )
