Flask-Storm
===========
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

    $ pip install flask_storm


Documentation
-------------
To use Flask Storm the application must set the `STORM_DATABASE_URI` configuration variable to a `valid database URI <https://storm.canonical.com/Manual#Databases>`_.


Why not Python 3
----------------
Sadly Storm is not Python 3 compatible. Flask Storm however should be compatible once Storm is.


Planned expansions
------------------
adsf
