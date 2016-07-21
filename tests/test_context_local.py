import pytest

from flask_storm import store, create_context_local
from storm.locals import Store


require = pytest.mark.usefixtures


@require("app_context")
def test_context_local(flask_storm):
    assert isinstance(store._get_current_object(), Store)
    assert store._get_current_object() is flask_storm.store


def test_no_context():
    with pytest.raises(RuntimeError):
        store._get_current_object()


@require("app_context")
def test_wrong_context():
    with pytest.raises(RuntimeError):
        store._get_current_object()


def test_bind_context_local(app, flask_storm):
    app.config["STORM_BINDS"] = {
        "extra": app.config["STORM_DATABASE_URI"]
    }

    extra_store = create_context_local("extra")

    with app.app_context():
        assert extra_store._get_current_object() is flask_storm.get_store("extra")
