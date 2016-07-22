import pytest
import re
import sys

from datetime import datetime, timedelta
from flask_storm import store, FlaskStorm
from flask_storm.debug import DebugTracer, get_debug_queries, DebugQuery, ShellTracer
from mock import MagicMock, patch
from storm.exceptions import OperationalError
from threading import Thread

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

# Enable skipping of tests that do not run without sqlparse being installed
try:
    import sqlparse
except ImportError:
    sqlparse = None

require_sqlparse = pytest.mark.skipif(not sqlparse, reason="requires sqlparse")

require = pytest.mark.usefixtures


@require("app", "flask_storm", "app_context")
def test_get_debug_queries():
    with DebugTracer():
        store.execute("SELECT 1")
        store.execute("SELECT ? + ?", [1, 2])

    queries = get_debug_queries()
    assert len(queries) == 2

    first, second = queries
    assert first.statement == "SELECT 1"
    assert first.params == ()
    assert isinstance(first.start_time, datetime)
    assert isinstance(first.end_time, datetime)
    assert isinstance(first.duration, timedelta)

    assert second.statement == "SELECT ? + ?"
    assert second.params == [1, 2]


def test_debug_query():
    data = (
        "SELECT 1",
        (),
        datetime(2000, 1, 1),
        datetime(2000, 1, 1, second=1))
    dq = DebugQuery(*data)

    for i, value in enumerate(data):
        assert dq[i] == value


def test_debug_query_keys():
    dq = DebugQuery(
        "SELECT 1",
        (),
        datetime(2000, 1, 1),
        datetime(2000, 1, 1, second=1))

    assert dq.statement == "SELECT 1"
    assert dq.params == ()
    assert dq.start_time == datetime(2000, 1, 1)
    assert dq.end_time == datetime(2000, 1, 1, second=1)
    assert dq.duration == timedelta(seconds=1)


@require("flask_storm")
def test_tracer_thread_isolation(app, app_context):
    with DebugTracer():
        store.execute("SELECT 'this'")

        # Spawn a separate thread that also executes a query
        def other_request():
            with app.app_context():
                store.execute("SELECT 'other'")

                # Ensure main thread does not leak into this one
                queries = get_debug_queries()
                assert len(queries) == 1
                assert queries[0].statement == "SELECT 'other'"

        t = Thread(target=other_request)
        t.start()
        t.join()

    # Ensure query log was not polluted by other thread
    queries = get_debug_queries()
    assert len(queries) == 1
    assert queries[0].statement == "SELECT 'this'"


def test_get_debug_queries_no_context():
    assert get_debug_queries() == []


def test_query_without_context(app):
    fs = FlaskStorm(app)
    try:
        store = fs.connect()
        with DebugTracer():
            store.execute("SELECT 1")

        # Since no application context is available queries are not saved
        # anywhere
        assert get_debug_queries() == []
    finally:
        store.close()


@require("app_context", "flask_storm")
def test_query_error():
    try:
        with DebugTracer():
            store.execute("SELECT !")
    except Exception:
        pass

    queries = get_debug_queries()
    assert len(queries) == 1
    assert queries[0].statement == "SELECT !"


@require_sqlparse
@require("app_context", "flask_storm")
def test_shell_tracer():
    # Alias helper functions
    remove_whitespace = pytest.helpers.remove_whitespace
    remove_ansi = pytest.helpers.remove_ansi

    sql = "SELECT 1 + 1 FROM (SELECT 2 + 2)"

    output = StringIO()
    output.isatty = MagicMock(return_value=True)

    with patch("sys.platform", "linux2"), ShellTracer(file=output, fancy=True):
        store.execute(sql)

    color_output = output.getvalue()
    output.close()

    assert color_output != sql
    assert \
        remove_whitespace(remove_ansi(color_output)).rsplit(";", 1)[0] == \
        remove_whitespace(sql)

    output = StringIO()
    output.isatty = MagicMock(return_value=False)

    with ShellTracer(file=output, fancy=False):
        store.execute(sql)

    colorless_output = output.getvalue()
    output.close()

    assert color_output != colorless_output
    assert \
        remove_ansi(color_output).rsplit(";", 1)[0] == \
        colorless_output.rsplit(";", 1)[0]
    assert \
        remove_whitespace(remove_ansi(color_output)).rsplit(";", 1)[0] == \
        remove_whitespace(sql)

def test_shell_tracer_defaults():
    st = ShellTracer()

    assert st.file is sys.stdout
    assert st.fancy


@require("app_context", "flask_storm")
def test_shell_tracer_success():
    output = StringIO()

    with ShellTracer(file=output, fancy=False):
        store.execute("SELECT 1")

    assert "SUCCESS" in output.getvalue()
    output.close()


@require("app_context", "flask_storm")
def test_shell_tracer_failure():
    output = StringIO()

    with ShellTracer(file=output, fancy=False), pytest.raises(Exception):
        store.execute("SELECT !")

    assert "FAILURE" in output.getvalue()
    output.close()
