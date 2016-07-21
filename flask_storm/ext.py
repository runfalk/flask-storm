from flask import current_app, _app_ctx_stack
from storm.locals import create_database, Store

from .debug import ShellTracer
from .utils import find_flask_storm, create_context_local

class FlaskStorm(object):
    """
    Create a FlaskStorm instance.

    :param app: Application to enable Flask-Storm for. This is the same as
                calling :py:meth:`~FlaskStorm.init_app` after initialization.
    """

    _app = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        # Order is important here as init_app() checks that self._app is None
        self._app = app

    @property
    def app(self):
        if self._app is not None:
            return self._app
        return current_app

    @property
    def is_bound(self):
        return self._app is not None

    def init_app(self, app):
        """
        Binds this extension to the given application. This is important since
        the database connection will not close unless the application has been
        initialized.

        .. note::
           One instance of FlaskStorm may be registered to multiple
           applications. One application should however only be registered to
           one FlaskStorm instance, or tear down functionality will trigger
           multiple times.

        :param app: Application to enable Flask-Storm for.
        :raises RuntimeError: if an application is already bound to this
                              instance by being passed to the constructor.
        """

        # If this class was instanciated with an app as its argument this method
        # we fail because this instance is not dependent on application context
        if self.is_bound:
            raise RuntimeError(
                "This FlaskStorm instance is already strictly bound to an "
                "application. To use this instance with multiple applications "
                "do not pass an application to the constructor and call "
                "init_app() for every application")

        # Check if there is an existing FlaskStorm instance bound to this app
        flask_storm = find_flask_storm(app)
        if flask_storm is not None:
            raise ValueError(
                "FlaskStorm already registered for this application")

        # Register instance of self on the application object. This dictionary
        # has existed on the Flask class since 0.7, and we rely on the
        # application context, which came later. Hence there is no check for
        # whether the attribute exists or not
        app.extensions["storm"] = self

        # Register a shell context function to make the store application
        # context locally available. This also installs a debug tracer which
        # prints every query to STDOUT. This function is available from version
        # 0.11 of Flask and later
        if hasattr(app, "shell_context_processor"):
            @app.shell_context_processor
            def shell_context():
                tracer = ShellTracer(fancy=True)
                tracer.start()

                return {
                    "store": create_context_local(None),
                    "_store_tracer": tracer,
                }

        # Register teardown to make sure Store is closed at the end of each
        # request
        @app.teardown_appcontext
        def close_store(response_or_exception):
            ctx = _app_ctx_stack.top
            for store in getattr(ctx, "storm_store", {}).values():
                store.close()

    def get_binds(self):
        """
        Return dict of database URIs for the application as defined by the
        ``STORM_BINDS`` configuration variable. If ``STORM_DATABASE_URI`` is
        defined it will be available using the key ``None``.

        :return: Dict from bind names to database URIs.
        """

        binds = self.app.config.get("STORM_BINDS", {}).copy()
        # Check if None key exists since that is used for the default store
        if None in binds:
            raise RuntimeError(
                "There is a None key in STORM_BINDS. This is reserved for "
                "the default store as defined by STORM_DATABASE_URI")

        if "STORM_DATABASE_URI" in self.app.config:
            binds[None] = self.app.config.get("STORM_DATABASE_URI")

        return binds

    def connect(self, bind=None):
        """
        Return a new Store instance with a connection to the database specified
        in the STORM_DATABASE_URI configuration variable of the bound application.
        This method normally not be called externally as it does not close the
        store once the application context tears down.

        :param bind: Database URI to use, defaults to ``STORM_DATABASE_URI``.
                     See :py:meth:`.get_binds` for details.
        :return: Store instance
        :raises RuntimeError: if no connection URI is found.
        """

        binds = self.get_binds()
        if bind not in binds:
            raise RuntimeError(
                "No connection URI found in configuration. Is "
                "STORM_DATABASE_URI defined?")

        return Store(create_database(binds[bind]))

    def get_store(self, bind=None):
        """
        Return a Store instance for the current application context. If there is
        no instance a new one will be created. Instances created using this
        method will close on application context tear down.

        :param bind: Bind name of database URI. Defaults to the one specified by
                     ``STORM_DATABASE_URI``.
        :return: Store for the current application context.
        :raises RuntimeError: if accessed outside the scope of an application
                              context.
        """

        ctx = _app_ctx_stack.top
        if ctx is not None:
            # Create a dictionary where open store connections are stored
            if not hasattr(ctx, "storm_store"):
                ctx.storm_store = {}

            storm_store = ctx.storm_store
            if bind not in ctx.storm_store:
                ctx.storm_store[bind] = self.connect(bind)
            return ctx.storm_store[bind]

    store = property(get_store)
