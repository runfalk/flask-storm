Changelog
=========
Version are structured like the following: ``<major>.<minor>.<bugfix>``. Unless
explicitly stated, changes are made by
`Andreas Runfalk <https://github.com/runfalk>`_.


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
