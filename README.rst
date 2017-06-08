Flask-Storm
===========
|test-status| |documentation-status| |pypi-version|

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

    $ pip install flask_storm[fancy]

This installs Flask-Storm with SQL highlighting and reformatting support. If you do not want this drop the ``fancy``.

.. code-block:: bash

    $ pip install flask_storm

Documentation
-------------
Documentation is available on `<http://flask-storm.readthedocs.io/>`_


Why not Python 3
----------------
Sadly Storm is not Python 3 compatible, which is why it doesn't make sense to make Flask-Storm compatible yet.

.. |test-status| image:: https://travis-ci.org/runfalk/flask-storm.svg
    :alt: Test status
    :scale: 100%
    :target: https://travis-ci.org/runfalk/Flask-Storm

.. |documentation-status| image:: https://readthedocs.org/projects/flask-storm/badge/
    :alt: Documentation status
    :scale: 100%
    :target: http://flask-storm.readthedocs.io/

.. |pypi-version| image:: https://badge.fury.io/py/Flask-Storm.svg
    :alt: PyPI version status
    :scale: 100%
    :target: https://pypi.python.org/pypi/Flask-Storm/

.. Include changelog on PyPI

.. include:: doc/changelog.rst
