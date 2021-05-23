Documentation
=============
Flask-Storm is an extension for `Flask <https://www.palletsprojects.com/p/flask/>`_ that adds support for Canonical's ORM `Storm <https://storm.canonical.com/>`_ to your application. Flask-Storm automatically opens and closes database connections on demand when requests need them.


Quickstart
----------
This will be a quick example of how to use Flask-Storm to create a REST API endpoint for a list of messages. For the full example code, see `Full example.py`_.

Imports
~~~~~~~~~
.. literalinclude:: ../example.py
   :lines: 1-5
   :emphasize-lines: 3

To get a minimal application running there are a few needed imports. The only noteworthy thing here is the :attr:`~flask_storm.store` context local. For a primer on context locals see the `flask documentation <http://flask.pocoo.org/docs/0.11/appcontext/>`_. This variable is a bit magic, and works just like the built-in `g <http://flask.pocoo.org/docs/0.11/api/#flask.g>`_.

Application setup
~~~~~~~~~~~~~~~~~
.. literalinclude:: ../example.py
   :lines: 8-12

Flask-Storm needs the ``STORM_DATABASE_URI`` to know which database to connect to. The format is described in the `official documentation <https://storm.canonical.com/Manual#The_create_database.28.29_function>`_ for Storm. It does not matter when the configuration variable is set, as long as it is done before using the :attr:`~flask_storm.store` context local. Flask-Storm is bound to a Flask application by using :meth:`~flask_storm.FlaskStorm.init_app`. One instane of :class:`~flask_storm.FlaskStorm` can be bound to multiple applications at once. One application can however only be bound to a single :class:`~flask_storm.FlaskStorm` instance.

Declaring a model
~~~~~~~~~~~~~~~~~
.. literalinclude:: ../example.py
   :lines: 15-27

This is how a model is declared in Storm. In this case a Post has an integer ``id`` column as primary key, and two Unicode text columns; ``name`` and ``text``. The table ``posts`` is declared using a special dunderscore ``__storm_table__``.

Initializing the database
~~~~~~~~~~~~~~~~~~~~~~~~~
.. literalinclude:: ../example.py
   :lines: 30-52

Starting with Flask version 0.11 there is a default `command line interface <http://flask.pocoo.org/docs/0.11/cli/>`_ that one can hook into. To create all tables and fill them with sample data, it is just a matter of running:

.. code-block:: bash

   FLASK_APP=example.py flask initdb

The command will create ``test.db`` with the schema and data. This is the first use of an actual connection to the database. Note that there is no need to connect or close the store. This is handled automatically by Flask-Storm. A connection is never opened until the :attr:`~flask_storm.store` context local is accessed, and remains open until the application context is torn down.

Serving requests
~~~~~~~~~~~~~~~~
.. literalinclude:: ../example.py
   :lines: 55-

The route serves a JSON array response containing the last 10 posts. In this case it is post 6 through 15.

Now it is just a matter of running the application. This is easily done using the Flask command line interface:

.. code-block:: bash

   FLASK_APP=example.py flask run

This will, if there are no errors, serve the application on `<http://localhost:5000/>`_. Open this page in a web-browser to see the JSON data.


Setup and tear down procedure
-----------------------------
To prevent unnecessary overhead, database connections are created on demand when used within the `application context <http://flask.pocoo.org/docs/0.11/appcontext/>`_. The same connection gets reused, and remains open, until the application context is torn down.

This means the only thing required to use the :attr:`~flask_storm.store` context local is a configured application context.


Configuration options
---------------------
This is the full list of configuration options for Flask Storm.

``STORM_DATABASE_URI``
  URI for the default database to connect to. This has the same format as the argument to Storm's ``create_database`` as defined in the `official documentation <https://storm.canonical.com/Manual#The_create_database.28.29_function>`_.

``STORM_BINDS``
  A dictionary of Storm URIs that Flask Storm can connect to. A bind is defined as an arbitrary key, used to identify the bind, and a URI for the database. See `Using with multiple Stores`_ for an in-depth explaination.


Using with Flask CLI
--------------------
When using ``flask shell``, Flask Storm will automatically provide a refence to the :attr:`~flask_storm.store` context local. Flask Storm also sets up debug output of the SQL statements created by Storm. This makes ``flask shell`` a good testing environment for building complex queries with Storm.

To make things more convenient it is recommended to provide model objects directly to the shell context. This is done easily by adding them using a shell context processor.

.. code-block:: python

    from flask import Flask
    from storm.locals import Int, Unicode

    class User(object):
        __storm_table__ = "users"

        id = Int(primary=True)
        name = Unicode()

    app = Flask("example")

    @app.shell_context_processor
    def shell_context():
        return {"User": User}

This example makes automatically makes ``User`` available in the shell environment.

.. note::
   It is possible to disable SQL statement printing by calling stop on the tracer.

       >>> _storm_tracer.stop()

   To disable color printing, reset the ``fancy`` flag:

       >>> _storm_tracer.fancy = False


Using with multiple Stores
--------------------------
To interface with multiple Stores simultaneously binds exist. Apart from the default database, declared in ``STORM_DATABASE_URI``, an arbitrary number of extra databases can be declared in ``STORM_BINDS``. A bind declaration may look something like this:

.. code-block:: python

    STORM_BINDS = {
        "extra": "sqlite://:memory:",
    }

The key ``extra`` is used to reference the bind, and the URI is used when connecting to the database. To make binds as easy to use as the normal :attr:`~flask_storm.store` context local it is possible to create context locals for every bind, using :func:`~flask_storm.create_context_local`.

.. code-block:: python

    # Use the same key as when declaring the bind. In this case "extra"
    extra_store = create_context_local("extra")

``extra_store`` can now be used just like :attr:`~flask_storm.store` as long as an application context is available. Just like the default store, all binds are automatically closed on application context teardown.

.. tip::
   Declare extra bind context locals in a separate Python file that can be imported.


Full example.py
---------------
.. literalinclude:: ../example.py
