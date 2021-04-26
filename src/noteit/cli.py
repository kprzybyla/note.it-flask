__all__ = []

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from .model import db
from .app import create_app
from .commands import RemoveExpired


def cli() -> None:
    """
    Command line interface for managing the flask app.
    """

    app = create_app()
    _ = Migrate(app, db)

    manager = Manager(app)
    manager.add_command("db", MigrateCommand)
    manager.add_command("rm-expired", RemoveExpired)
    manager.run()
