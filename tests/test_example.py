from pathlib import Path
from runpy import run_path

import pytest


@pytest.fixture
def example_app(tmp_path):
    example = run_path(str(Path(__file__).resolve().parents[1] / "example.py"))
    app = example["app"]
    app.config.update(
        TESTING=True,
        STORM_DATABASE_URI=f"sqlite:///{tmp_path / 'posts.db'}",
    )
    return app


@pytest.fixture
def initialized_app(example_app):
    result = example_app.test_cli_runner().invoke(args=["initdb"])
    assert result.exit_code == 0, result.output
    return example_app


def test_index_returns_ten_latest_posts(initialized_app):
    client = initialized_app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.is_json
    posts = response.get_json()
    assert [post["id"] for post in posts] == list(range(15, 5, -1))
    for post in posts:
        assert set(post) == {"id", "name", "text"}
        assert post["name"] in {"Alice", "Bob", "Eve"}
        assert post["text"] == f"Post #{post['id']}"

    assert client.get("/").get_json() == posts
