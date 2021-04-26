__all__ = ["RemoveExpired"]

import datetime

from typing import Final

from flask_script import Command

from ..model import db, Note

TRUTH_TABLE: Final[list[str]] = ["y", "Y", "yes", "YES"]


class RemoveExpired(Command):

    """
    Command for removing notes from database if they are expired.
    """

    __slots__ = ()

    def run(self) -> None:
        current_date = datetime.datetime.now()

        query = db.session.query(Note).filter(Note.expiration_date < current_date)
        notes = query.count()

        if not notes:
            print("There are no expired notes in the database")
        else:
            print(f"Current date: {current_date}")
            print(f"Are you sure you want to remove {notes} note(s) that expired? (y/N)")

            try:
                answer = input()
            except KeyboardInterrupt:
                pass
            else:
                if answer in TRUTH_TABLE:
                    query.delete()
                    db.session.commit()
                    print(f"Removed {notes} note(s)")
                else:
                    print(f"Will keep {notes} note(s)")
