from random import choice

from flask import Flask, jsonify
from storm.locals import Desc, Int, Unicode

from flask_storm import FlaskStorm, store

app = Flask("example")
app.config["STORM_DATABASE_URI"] = "sqlite:///test.db"

flask_storm = FlaskStorm()
flask_storm.init_app(app)


class Post:
    __storm_table__ = "posts"

    id = Int(primary=True)
    name = Unicode()
    text = Unicode()

    def __init__(self, name=None, text=None):
        if name is not None:
            self.name = name

        if text is not None:
            self.text = text


@app.cli.command()
def initdb():
    """Create schema and fill database with 15 sample posts by random authors"""

    store.execute("""DROP TABLE IF EXISTS posts""")
    store.execute("""
        CREATE TABLE posts(
            id    INTEGER PRIMARY KEY,
            name  VARCHAR,
            text  VARCHAR
        )
    """)

    names = [
        "Alice",
        "Bob",
        "Eve",
    ]

    for i in range(1, 16):
        store.add(Post(choice(names), f"Post #{i}"))

    store.commit()


@app.route("/")
def index():
    """Return the 10 latest posts in JSON format"""

    return jsonify(
        [
            {
                "id": post.id,
                "name": post.name,
                "text": post.text,
            }
            for post in store.find(Post).order_by(Desc(Post.id)).config(limit=10)
        ]
    )
