import pytest
import sys

from flask_storm.utils import colored, has_color_support
from mock import Mock, patch


fg42 = "\x1b[38;5;42m"
bg69 = "\x1b[48;5;69m"
bold = "\x1b[1m"
underline = "\x1b[4m"
reset = "\x1b[0m"


def j(*args):
    return "".join(args)


def test_reset():
    assert len(colored("")) == 0
    assert colored("", bold=True).endswith("\x1b[0m")


def test_foreground_color():
    assert colored("foo", color=42) == j(fg42, "foo", reset)


def test_background_color():
    assert colored("foo", background=69) == j(bg69, "foo", reset)


def test_bold():
    assert colored("foo", bold=True) == j(bold, "foo", reset)


def test_underline():
    assert colored("foo", underline=True) == j(underline, "foo", reset)


def test_prefix_order():
    ansi = colored("foo", color=42, background=69, bold=True, underline=True)
    real = j(fg42, bg69, bold, underline, "foo", reset)
    assert ansi == real


def test_has_color_support():
    tty_file = Mock()
    tty_file.isatty.return_value = True

    file = Mock()
    file.isatty.return_value = False

    with patch("sys.platform", "Pocket PC"):
        assert not has_color_support(tty_file)

        # This will check against STDOUT, but will always fail because of the
        # Pocket PC platform
        assert not has_color_support()

    with patch("sys.platform", "darwin"):
        assert has_color_support(tty_file)
        assert not has_color_support(file)

    with patch("sys.platform", "linux2"):
        assert has_color_support(tty_file)
        assert not has_color_support(file)

    with patch("sys.platform", "win32"):
        assert not has_color_support(tty_file)
        with patch.dict("os.environ", {"ANSICON": ""}):
            assert has_color_support(tty_file)

