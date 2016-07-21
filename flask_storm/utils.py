import datetime as dt
import os
import sys

from collections import MutableMapping
from flask import current_app
from functools import partial
from storm.variables import Variable
from werkzeug.local import LocalProxy


def find_flask_storm(app):
    """
    Find and return :py:class:`FlaskStorm` instance for the given application.

    :param app: Application to look for FlaskStorm instance in.
    :return: FlaskStorm instance if found, else None.
    """

    return getattr(app, "extensions", {}).get("storm")


def _lookup_storm_store(bind=None):
    app = current_app
    if not app:
        raise RuntimeError("Working outside an application context")

    flask_storm = find_flask_storm(app)
    if flask_storm is None:
        raise RuntimeError("FlaskStorm is not bound to the current application")

    return flask_storm.get_store(bind)


def create_context_local(bind):
    """
    Create a context local for the given bind. None means the default store.

    ::

        # Context local for the bind report_store
        report_store = create_context_local("report_store")

    This is what is used to implement the store context local which analogue to

    ::

        store = create_context_local(None)

    :param bind: Bind name of database URI to use when creating store.
    :raises RuntimeError: if working outside application context or if
                          FlaskStorm is not bound to the current application.

    """

    return LocalProxy(partial(_lookup_storm_store, bind))


def has_color_support(file=None):
    """
    Determine if terminal has color support. Code borrowed from
    django.core.management.color.supports_color().

    :return: True if color is supported, else False
    """

    if file is None:
        file = sys.stdout

    supported_platform = sys.platform != "Pocket PC" and (
        sys.platform != "win32" or "ANSICON" in os.environ)
    is_tty = getattr(file, "isatty", lambda: False)()

    return supported_platform and is_tty


def colored(msg, color=None, background=None, bold=None, underline=None):
    """
    Return string formatted using ANSI escape codes. Supports 256 colors.

    https://upload.wikimedia.org/wikipedia/en/1/15/Xterm_256color_chart.svg

    :param string: String to format.
    :param color: Color of text.
    :param background: Color of background.
    :param bold: True if text should be bold.
    :param underline: True if text should be underlined.
    """

    prefix = ""

    if color is not None:
        prefix += "\x1b[38;5;{}m".format(color)

    if background is not None:
        prefix += "\x1b[48;5;{}m".format(background)

    if bold:
        prefix += "\x1b[1m"

    if underline:
        prefix += "\x1b[4m"

    suffix = ""
    if prefix:
        suffix = "\x1b[0m"

    return "{}{}{}".format(prefix, msg, suffix)
