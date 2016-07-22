import pytest
import re

from flask import Flask
from flask_storm import FlaskStorm


pytest_plugins = [
    "helpers_namespace",
]


@pytest.fixture
def app(request):
    app = Flask("foo")
    app.config["STORM_DATABASE_URI"] = "sqlite://:memory:"
    return app


@pytest.fixture
def flask_storm(app):
    # The app here will be the same app instance if requested by the test
    # function due to the scoping nature of py.test
    flask_storm = FlaskStorm()
    flask_storm.init_app(app)
    return flask_storm

@pytest.yield_fixture
def app_context(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.helpers.register
def remove_whitespace(string):
    return re.sub(r"\s+", "", string)


@pytest.helpers.register
def remove_ansi(string):
    return re.sub(r"\x1b\[[^m]+m", "", string)
