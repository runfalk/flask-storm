Changelog
=========
Version are structured like the following: ``<major>.<minor>.<bugfix>``. Unless
explicitly stated, changes are made by
`Andreas Runfalk <https://github.com/runfalk>`_.


Version 2.0.0
-------------
Released on Oct 25th, 2026.

This release has **breaking changes**. It drops support for EOL Python versions
and drops support for old Flask versions.

- Require ``flask>=2.2`` since the old hack to add an object to Flask's
  application doesn't work with modern flask versions. It's now using the
  documented ``flask.globals.app_ctx`` which was introduced in this release.
  Thank you `lgp171188 <https://github.com/lgp171188>`_ for
  `submitting a fix <https://github.com/runfalk/flask-storm/pull/3>`_.
- Dropped support for Python 3.6
- Dropped support for Python 3.7
- Dropped support for Python 3.8
- Dropped support for Python 3.9
- Dropped support for Python 3.10
- Added support for Python 3.11
- Added support for Python 3.12
- Added support for Python 3.13
- Added support for Python 3.14
- Added support for Python 3.15
- Remove explicit unicode literals ``u""`` as no supported versions require
  them.
- Replace ``str.format`` with f-strings as all supported versions can use them.
- Removed the old Python 2 ``_compat`` module.
- Replaced setuptools packaging with ``uv``.
- ``__version__`` is now backed by the value in ``pyproject.toml`` using
  ``importlib.metadata``.
- Dropped support for the archived ``storm-legacy`` package and restored
  upstream ``storm`` as a required dependency.
- Replaced ``black`` and ``flake8`` development dependencies with ``ruff``.
- Removed ``tox`` and use CI matrices for testing across multiple Python
  versions.
- Removed generated comments, unused settings, and redundant defaults from the
  Sphinx configuration.
- Removed the unused documentation Makefile and obsolete documentation build
  exclusions. Documentation is built directly with ``uv run sphinx-build``.
- Added integration tests for ``example.py``, covering database initialization,
  resetting existing data, and returning the ten latest posts as JSON.
- Fix broken ``example.py``


Version 1.0.0
-------------
Released on 23rd May 2021

- Dropped support for Python 3.3
- Dropped support for Python 3.4
- Dropped support for Python 3.5
- Updated documentation to work with newer Sphinx versions
- Support upstream Storm 0.21 or newer (thank you
  `Colin Watson <https://github.com/cjwatson>`_)
- Fixed broken placeholder replacement when using SQL statement printing in
  Python 3 (thank you `Colin Watson <https://github.com/cjwatson>`_)
- Fixed problem where ``fancy`` would always be set to ``False`` regardless of
  the provided value when it was specified to a tracer.

Note that dropped Python versions may still work, but that's accidental rather
than intentional.


Version 0.2.0
-------------
Released on 8th October 2018

- Added Python 3 support
- Removed ``storm`` as a dependency since ``storm-legacy`` can be used as well


Version 0.1.2
-------------
Released on 14th June 2017

- Fixed an issue with query logging in ``flask shell`` and PostgreSQL


Version 0.1.1
-------------
Released on 9th June 2017

- Fixed issue with new versions of sqlparse by bumping its version requirement


Version 0.1.0
-------------
Released on 19 July 2016

- Initial release
