import pytest

from flask.testing import FlaskClient

from noteit.app import create_app
from noteit.model import db

from .database import Database


@pytest.fixture(scope="module")
def database() -> None:
    with Database() as database:
        yield database


@pytest.fixture(scope="module")
def tester(database: Database) -> FlaskClient:
    app = create_app(database=database.uri)
    app.debug = True
    app.testing = True

    with app.app_context():
        with app.test_client() as client:
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()
