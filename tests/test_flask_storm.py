import pytest

from flask import Flask, current_app
from flask_storm import FlaskStorm, find_flask_storm
from mock import patch
from storm.locals import Store

require = pytest.mark.usefixtures


def test_find_flask_storm(app, flask_storm):
    assert find_flask_storm(app) is flask_storm


def test_duplicate_init(app, flask_storm):
    with pytest.raises(ValueError):
        flask_storm.init_app(app)

    with pytest.raises(ValueError):
        fs = FlaskStorm()
        fs.init_app(app)


def test_already_bound_init_app(app):
    flask_storm = FlaskStorm(app)
    with pytest.raises(RuntimeError):
        flask_storm.init_app(Flask("bar"))


def test_is_bound_init_app(app):
    fs = FlaskStorm()
    assert not fs.is_bound

    fs.init_app(app)
    assert not fs.is_bound


def test_is_bound(app):
    fs = FlaskStorm(app)
    assert fs.is_bound


@require("app_context")
def test_get_binds(app, flask_storm):
    memory_uri = app.config["STORM_DATABASE_URI"]

    assert flask_storm.get_binds() == {None: memory_uri}

    bind_uri = memory_uri + "?extra_param"
    app.config["STORM_BINDS"] = {"extra": bind_uri}
    assert flask_storm.get_binds() == {
        None: memory_uri,
        "extra": bind_uri
    }

@require("app_context")
def test_none_in_binds(app, flask_storm):
    app.config["STORM_BINDS"] = {
        None: app.config["STORM_DATABASE_URI"],
    }

    with pytest.raises(RuntimeError):
        flask_storm.get_binds()


@require("app_context")
def test_connect(app, flask_storm):
    store = flask_storm.connect()
    try:
        assert isinstance(store, Store)
    finally:
        store.close()


@require("app_context")
def test_connect_no_binds(app, flask_storm):
    app.config.pop("STORM_DATABASE_URI")

    with pytest.raises(RuntimeError):
        flask_storm.connect()


@require("app_context")
def test_connect_binds(app, flask_storm):
    # Remove configuration key for test
    memory_uri = app.config.pop("STORM_DATABASE_URI")

    app.config["STORM_BINDS"] = {
        "memory": memory_uri
    }

    with pytest.raises(RuntimeError):
        flask_storm.connect()

    store = flask_storm.connect("memory")
    try:
        assert isinstance(store, Store)
    finally:
        store.close()


def test_teardown(app, flask_storm):
    ctx = app.app_context()
    ctx.push()

    real_store = flask_storm.store

    with patch.object(real_store, "close", wraps=real_store.close) as mock:
        # Assert teardown is not called before application context is gone
        assert not mock.called

        # Teardown application context
        ctx.pop()

        # Make sure store was closed after application context teardown
        assert mock.called

def test_teardown_binds(app, flask_storm):
    app.config["STORM_BINDS"] = {
        "extra": app.config["STORM_DATABASE_URI"]
    }

    ctx = app.app_context()
    ctx.push()

    real_store = flask_storm.get_store()
    extra_store = flask_storm.get_store("extra")

    patch_real_store = patch.object(real_store, "close", wraps=real_store.close)
    patch_extra_store = patch.object(
        extra_store, "close", wraps=extra_store.close)
    with patch_real_store as store_mock, patch_extra_store as extra_mock:
        # Assert teardown is not called before application context is gone
        assert not store_mock.called
        assert not extra_mock.called

        # Teardown application context
        ctx.pop()

        # Make sure stores were closed after application context teardown
        assert store_mock.called
        assert extra_mock.called


@require("flask_storm")
def test_shell_context(app):
    ctx = app.make_shell_context()
    try:
        assert "store" in ctx
        assert "_store_tracer" in ctx
    finally:
        ctx["_store_tracer"].stop()
