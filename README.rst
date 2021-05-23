Flask-Storm
===========
|test-status| |pypi-version|

Flask-Storm is an extension for `Flask <https://www.palletsprojects.com/p/flask/>`_ that adds support for Canonical's ORM `Storm <https://storm.canonical.com/>`_ to your application. Flask-Storm automatically opens and closes database connections on demand when requests need them.


Example
-------
Access to the database is done using the `store` `application context local <http://flask.pocoo.org/docs/0.11/appcontext/>`_. Within an application context this variable holds a reference to a Storm Store instance. If no connection is opened it will automatically open one. When the application context is torn down, normally after the request has returned, the store is closed.

.. code-block:: python

    from flask_storm import store
    from storm.locals import Int, Unicode

    class User(object):
        __storm_table__ = "users"

        id = Int(primary=True)
        name = Unicode()


    @app.route("/")
    def index():
        # Get name of user with ID 1
        return store.get(User, 1).name


Installation
------------

.. code-block:: bash

    pip install flask_storm[fancy]

This installs Flask-Storm with SQL highlighting and reformatting support. If you do not want this drop the ``fancy``.

.. code-block:: bash

    pip install flask_storm


Documentation
-------------
Documentation is available on `<https://runfalk.github.io/flask-storm>`_


Development
-----------

.. code-block:: bash

    # Setup environment
    python3 -m venv --prompt=flask-storm .venv
    source .venv/bin/activate
    pip install --upgrade pip setuptools
    pip install -e .[dev,fancy]

    # Run test suite
    pytest

    # You can test all supported python versions in one go using tox
    tox

    # Build documentation
    sphinx-build doc/ doc-build/

    # Run auto formatter
    black flask_storm/ tests/ setup.py

    # Run linter
    flake8 flask_storm/ tests/ setup.py


.. |test-status| image:: https://github.com/runfalk/flask-storm/actions/workflows/ci.yml/badge.svg
    :alt: Test status
    :scale: 100%
    :target: https://travis-ci.org/runfalk/Flask-Storm

.. |pypi-version| image:: https://badge.fury.io/py/Flask-Storm.svg
    :alt: PyPI version status
    :scale: 100%
    :target: https://pypi.python.org/pypi/Flask-Storm/

.. Include changelog on PyPI

.. include:: doc/changelog.rst
