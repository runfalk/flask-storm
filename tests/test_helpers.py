import pytest

def remove_whitespace():
    assert pytest.helpers.remove_whitespace("foo  bar") == "foobar"
    assert pytest.helpers.remove_whitespace("foo\t\tbar") == "foobar"
    assert pytest.helpers.remove_whitespace("foo\n\nbar") == "foobar"
    assert pytest.helpers.remove_whitespace("foo\r\rbar") == "foobar"
    assert pytest.helpers.remove_whitespace("foo\r\nbar") == "foobar"


def remove_ansi():
    assert pytest.helpers.remove_ansi("foo\x1b[0mbar") == "foobar"
    assert pytest.helpers.remove_ansi("foo\x1b[0bar") == "foo\x1b[0bar"
