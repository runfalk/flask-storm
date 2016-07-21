import pytest

from flask import Flask
from flask_storm import FlaskStorm

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
