import datetime
import textwrap

from typing import Final

from hypothesis import given, strategies as st

from noteit.model import Note

from .helpers import (
    valid_secret,
    valid_content,
    valid_expiration_date,
    DATE_FORMAT,
)

CONTENT_PREVIEW_LENGTH: Final[int] = 20


def test_note_repr() -> None:
    secret = valid_secret()
    content = valid_content()
    expiration_date = valid_expiration_date()

    shorten_content = textwrap.shorten(content, width=CONTENT_PREVIEW_LENGTH)

    note = Note(secret=secret, content=content, expiration_date=expiration_date)
    note_repr = repr(note)

    assert secret not in note_repr
    assert shorten_content in note_repr
    assert expiration_date.strftime(DATE_FORMAT) in note_repr


@given(secret=st.text())
def test_note_does_not_store_plaintext_password(secret: str) -> None:
    note = Note(secret=secret, content=str(), expiration_date=datetime.datetime.now())

    assert secret != note.secret
    assert note.verify_secret(secret)
