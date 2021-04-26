__all__ = ["create_app", "get_database_uri"]

import os

from typing import Optional, Final
from flask import Flask

from .model import db
from .views import home, view

SECRET_KEY: Final[bytes] = b"\xa8>\xb1\xa1\x84q\xc7\x7f\xb4r2s\xa3\x9ctW/\xae\xa3\xc7"


def create_app(database: Optional[str] = None) -> Flask:
    """
    Factory for flask app.
    """

    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    app.config["SQLALCHEMY_DATABASE_URI"] = database or get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.add_url_rule("/", "home", home, methods=["GET", "POST"])
    app.add_url_rule("/<uid>", "view", view, methods=["GET", "POST"])

    db.init_app(app)

    return app


def get_database_uri() -> str:
    """
    Helper function for building the database uri from environment variables.
    """

    database = os.environ.get("POSTGRES_DB")
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    username = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")

    return f"postgresql://{username}:{password}@{host}:{port}/{database}"
