__all__ = ["db", "Note"]

import hashlib
import datetime
import textwrap

from typing import Final

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text, DateTime

from .forms import DATE_FORMAT
from .extras import UUID

SHA_256_LENGTH: Final[int] = 256
HEX_BITS_PER_CHAR: Final[int] = 4

NOTE_SECRET_MAXIMUM_LENGTH: Final[int] = SHA_256_LENGTH // HEX_BITS_PER_CHAR
NOTE_CONTENT_PREVIEW_LENGTH: Final[int] = 20

db: Final[SQLAlchemy] = SQLAlchemy()


def _encode_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


class Note(db.Model):

    """
    Model for the note object.

    - UID contains the UUID
    - Secret contains the SHA-256 hash of password for the note
    - Content contains the note content
    - Post date contains the date on which the note was posted
    - Expiration date contains the date on which the nate will expire
    """

    __tablename__ = "note"

    uid = Column(UUID(), primary_key=True, unique=True, default=UUID.random)
    secret = Column(String(length=NOTE_SECRET_MAXIMUM_LENGTH))
    content = Column(Text())
    post_date = Column(DateTime(), default=datetime.datetime.now)
    expiration_date = Column(DateTime())

    def __init__(
        self,
        secret: str,
        content: str,
        expiration_date: datetime.datetime,
    ) -> None:
        self.secret = _encode_secret(secret)
        self.content = content
        self.expiration_date = expiration_date

    def __repr__(self) -> str:
        content = textwrap.shorten(self.content, width=NOTE_CONTENT_PREVIEW_LENGTH)

        args = [
            f"uid={self.uid}",
            f"secret={self.secret}",
            f"content={content}",
            f"post_date={self.post_date}",
            f"expiration_date={self.expiration_date.strftime(DATE_FORMAT)}",
        ]

        return f"<Note({', '.join(args)})>"

    def verify_secret(self, secret: str) -> bool:
        """
        Method for verifing the note secret.

        :param secret: secret passed by the user
        """

        return _encode_secret(secret) == self.secret
