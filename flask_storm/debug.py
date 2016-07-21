import sys

from contextlib import contextmanager
from datetime import datetime
from flask import _app_ctx_stack, has_request_context, request
from operator import itemgetter
from storm.tracer import install_tracer, remove_tracer
from werkzeug.local import Local

from .sql import Adapter, replace_placeholders, format as format_sql, color as color_sql
from .utils import has_color_support, colored

try:
    import sqlparse
except ImportError:
    sqlparse = None


__all__ = [
    "DebugTracer",
    "get_debug_queries",
    "RequestTracer",
    "ShellTracer",
]


class DebugQuery(tuple):
    __slots__ = ()

    statement = property(itemgetter(0))
    params = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))

    @property
    def duration(self):
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time

    def __new__(cls, statement, params, start_time, end_time):
        return tuple.__new__(cls, [statement, params, start_time, end_time])


class DebugTracer(object):
    """
    A tracer which stores all queries with parameters onto the current request
    context. Queries are accessible using :func:`get_debug_queries`. It is used
    as a context manager. Since all queries are stored on the request context,
    they can only be accessed until the current request tears down.

    ::

        with DebugTracer():
            # Perform queries
            queries = get_debug_queries()

    .. note::
       :func:`get_debug_queries` do not need to be called within the context
       manager, as long as the request context is still alive, since all queries
       are stored on the request context.
    """

    def __init__(self):
        # Use thread locals since the tracer gets installed globally. This
        # ensures start time will be correctly measured, even in multi-threaded
        # environments. Werkzeug's implementation is used instead of threading
        # from the standard library since Werkzeug supports greenlets as well.
        self.threadinfo = Local()

    def connection_raw_execute(self, connection, raw_cursor, statement, params):
        self.threadinfo.start_time = datetime.now()

    def connection_raw_execute_success(
            self, connection, raw_cursor, statement, params):

        ctx = _app_ctx_stack.top
        if ctx is None:
            return

        if not hasattr(ctx, "storm_debug_queries"):
            ctx.storm_debug_queries = []

        ctx.storm_debug_queries.append(DebugQuery(
            statement,
            params,
            getattr(self.threadinfo, "start_time"),
            datetime.now()))

        # Remove start time to prevent leakage across queries
        delattr(self.threadinfo, "start_time")

    def connection_raw_execute_error(
            self, connection, raw_cursor, statement, params, error):
        self.connection_raw_execute_success(
            connection, raw_cursor, statement, params)

    def __enter__(self):
        install_tracer(self)

    def __exit__(self, type, exception, traceback):
        remove_tracer(self)


def get_debug_queries():
    """
    Return an array of queries executed within the context of a
    :class:`DebugTracer` under the current application context and thread.
    """

    return getattr(_app_ctx_stack.top, "storm_debug_queries", [])


class ShellTracer(object):
    """
    :param file: File like object (has write method) where queries will be
                 logged to.
    :param fancy: When ``True`` (default) colored output is used, if support is
                  detected, when ``False`` plain text is used.
    """

    def __init__(self, file=None, fancy=None):
        if file is None:
            self.file = sys.stdout
        else:
            self.file = file

        self.fancy = False
        if fancy is None:
            self.fancy = True

        # Use thread locals since the tracer gets installed globally. This
        # ensures start time will be correctly measured, even in multi-threaded
        # environments. Werkzeug's implementation is used instead of threading
        # from the standard library since Werkzeug supports greenlets as well.
        self.threadinfo = Local()
        self.threadinfo.active = False

    @property
    def use_color(self):
        return self.fancy and has_color_support(self.file)

    def _log(self, msg):
        if not self.threadinfo.active:
            return

        self.file.write(
            u"{};\n".format(color_sql(msg) if self.use_color else msg))

    def _log_result(self, success):
        if not self.threadinfo.active:
            return

        time = self.threadinfo.end_time - self.threadinfo.start_time
        msg = u"-- {result} in {time} ms".format(
            result="SUCCESS" if success else "FAILURE",
            time=time.total_seconds() * 1000)

        self.file.write(u"{}\n".format(
            colored(msg, 244) if self.use_color else msg))

    def connection_raw_execute(self, connection, raw_cursor, statement, params):
        # Start timer after log printing since it may delay query execution and
        # skew the time
        self.threadinfo.start_time = datetime.now()

        if sqlparse is None:
            self._log(u"{}\n{!r}".format(statement, params))
        else:
            self._log(format_sql(
                replace_placeholders(statement, params, Adapter(connection))))

    def connection_raw_execute_success(
            self, connection, raw_cursor, statement, params):
        self.threadinfo.end_time = datetime.now()
        self._log_result(True)

    def connection_raw_execute_error(
            self, connection, raw_cursor, statement, params, error):
        self.threadinfo.end_time = datetime.now()
        self._log_result(False)

    def start(self):
        """
        Install and activate this tracer for all statements executed in this
        thread (or greenlet).
        """

        # We also need to indicate which particular thread this is installed for
        # since it will write for all threads unless told not to
        self.threadinfo.active = True

        install_tracer(self)

    def stop(self):
        """
        Stop using this tracer.
        """

        remove_tracer(self)
        self.threadinfo.active = False

    def __enter__(self):
        self.start()

    def __exit__(self, type, exception, traceback):
        self.stop()


class RequestTracer(ShellTracer):
    """
    A tracer which prints all SQL queries generated by Storm directly to STDOUT.
    This is useful when debugging views in flask.

    ::

        with RequestTracer():
            # Queries executed here will be printed into STDOUT
            ...

    :param file: File like object (has write method) where queries will be
                 logged to.
    :param fancy: When ``True`` (default) colored output is used, if support is
                  detected, when ``False`` plain text is used.
    """

    def _get_request_line(self, request):
        template = (
            '{ip} - - [{timestamp:%d/%b/%Y %H:%M:%S}] '
            '"{method} {path} {version}" SQL -\n')

        full_path = request.path
        if request.args:
            full_path += "?" + request.environ.get("QUERY_STRING")

        return template.format(
            ip=request.remote_addr,
            timestamp=datetime.now(),
            method=request.method,
            path=full_path,
            version=request.environ.get("SERVER_PROTOCOL"))

    def _log(self, msg):
        if has_request_context():
            self.file.write(self._get_request_line(request))
        super(RequestTracer, self)._log(msg)
