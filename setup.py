#!/usr/bin/env python
import re
import os

from setuptools import setup


class RstPreProcessor(object):
    def __init__(self):
        self.roles = {}
        self.blocks = {}
        self.replaces = {}

    def add_block(self, block, callback=None):
        if callback is None:
            def wrapper(callback):
                self.add_block(block, callback)
                return callback
            return wrapper
        self.blocks[block] = callback

    def add_role(self, role, callback=None):
        if callback is None:
            def wrapper(callback):
                self.add_role(role, callback)
                return callback
            return wrapper
        self.roles[role] = callback

    def add_replacement(self, search, replacement):
        self.replaces[search] = replacement

    def _block_dispatch(self, match):
        if match.group("block") not in self.blocks:
            return match.group(0)

        return self.blocks[match.group("block")](
            self,
            match.group("block"),
            match.group("args"),
            match.group("extra"),
            match.group("content"))

    def _role_dispatch(self, match):
        if match.group(1) not in self.roles:
            return match.group(0)

        return self.roles[match.group("role")](
            self,
            match.group("role"),
            match.group("args"),
            match.group("content"))

    def process(self, text):
        # Process blocks
        text = re.sub(
            "\.\.\s+(?:(?P<extra>\S+)\s+)?(?P<block>[^\n:]+)::"
            "\s+(?P<args>[^\n]+)(?:\n\n?(?P<content>.*?)\n\n(?=\S))?",
            self._block_dispatch,
            text,
            flags=re.DOTALL)

        # Process roles
        text = re.sub(
            ":(?P<role>[A-Za-z0-9_]+)(?:\s+(?P<args>[A-Za-z0-9_]+))?:"
            "`(?P<content>[^`]*)`",
            self._role_dispatch,
            text,
            flags=re.MULTILINE)

        # Run replaces
        for search, replacement in self.replaces.items():
            text = text.replace(search, replacement)

        return text


rst_pre_processor = RstPreProcessor()

@rst_pre_processor.add_role("class")
@rst_pre_processor.add_role("attr")
@rst_pre_processor.add_role("meth")
def role_simplyfier(processor, role, argument, content):
    format = {
        "attr": "``.{}``",
        "meth": "``{}()``",
    }

    if content.startswith("~"):
        return format.get(role, "``{}``").format(content[1:].split(".")[-1])
    else:
        return format.get(role, "``{}``").format(content + extra.get(role, ""))


@rst_pre_processor.add_block("include")
def includer(processor, block, args, extra, content):
    with open(args) as fp:
        return fp.read().rstrip()


with open("README.rst") as fp:
    long_desc = rst_pre_processor.process(fp.read())

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
        packages=["flask_storm"],
        platforms="any",
        install_requires=[
            "Flask",
            "storm"
        ],
        extras_require={
            "dev": [
                "mock",
                "pytest>=3",
                "pytest-cov",
                "pytest-helpers-namespace",
                "sphinx",
            ],
            "fancy": [
                "sqlparse>=0.2.2",
            ],
        },
        classifiers=(
            "Development Status :: 3 - Alpha",
            "Framework :: Flask",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Topic :: Database",
            "Topic :: Utilities",
            "Topic :: Software Development :: Libraries",
        ),
        zip_safe=False,
    )
