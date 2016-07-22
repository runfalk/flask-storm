import pytest
import sys

from datetime import date
from flask_storm.sql import default_adapter, replace_placeholders, format, color
from mock import patch

# Enable skipping of tests that do not run without sqlparse being installed
try:
    import sqlparse
except ImportError:
    sqlparse = None

require_sqlparse = pytest.mark.skipif(not sqlparse, reason="requires sqlparse")


def test_adapter_type():
    assert default_adapter.type is None


def test_adapter_str():
    assert default_adapter.adapt(u"foobar") == u"'foobar'"
    assert default_adapter.adapt(u"foo'bar") == u"'foo''bar'"
    assert default_adapter.adapt(ur"foo\'bar") == ur"'foo\\''bar'"


def test_adapter_bool():
    assert default_adapter.adapt(True) == u"TRUE"
    assert default_adapter.adapt(False) == u"FALSE"


def test_adapter_none():
    assert default_adapter.adapt(None) == u"NULL"


def test_adapter_int():
    assert default_adapter.adapt(42) == u"42"
    assert default_adapter.adapt(sys.maxint) == str(sys.maxint)

    # Trigger long type
    assert default_adapter.adapt(sys.maxint + 1) == str(sys.maxint + 1)


def test_adapter_float():
    assert default_adapter.adapt(1.5) == u"1.5"


def test_adapter_date():
    d = date.today()
    assert default_adapter.adapt(d) == default_adapter.adapt(str(d))

@require_sqlparse
def test_replace_placeholders():
    assert replace_placeholders("SELECT ? + ?", [1, 2]) == "SELECT 1 + 2"
    assert replace_placeholders("SELECT ?  +  ?", [1, 2]) == "SELECT 1  +  2"


@require_sqlparse
def test_replace_placeholders_exausted_params():
    with pytest.raises(ValueError):
        replace_placeholders("SELECT ?", [])

@require_sqlparse
def test_format():
    sql = "SELECT * FROM test t WHERE t.id > 10"
    fsql = format(sql)

    assert fsql != sql
    assert \
        pytest.helpers.remove_whitespace(fsql) == \
        pytest.helpers.remove_whitespace(sql)


def test_format_no_sqlparse():
    sql = "SELECT * FROM test t WHERE t.id > 10"
    with patch("flask_storm.sql.sqlparse", None):
        assert sql == format(sql)

@require_sqlparse
def test_color():
    sql = """
        SELECT *
        FROM test t
        WHERE t.id > 10 AND t.name = 'foobar'
        ORDER BY lower(t.name)
    """
    csql = color(sql)

    assert csql != sql
    assert pytest.helpers.remove_ansi(csql) == sql


def test_color_no_sqlparse():
    sql = """
        SELECT *
        FROM test t
        WHERE t.id > 10 AND t.name = 'foobar'
        ORDER BY lower(t.name)
    """

    with patch("flask_storm.sql.sqlparse", None):
        assert sql == color(sql)
