__all__ = [
    "date_expired",
    "CreateNoteForm",
    "AccessNoteForm",
    "DATE_FORMAT",
    "INCORRECT_SECRET_ERROR",
]

import string
import datetime

from typing import Optional, Final

from wtforms import (
    Form,
    Field,
    TextAreaField,
    PasswordField,
    DateTimeField,
    ValidationError,
    validators,
)

DATE_FORMAT: Final[str] = "%d-%m-%Y, %H:%M:%S"

SECRET_MINIMUM_LENGTH: Final[int] = 8
CONTENT_MAXIMUM_LENGTH: Final[int] = 500

# fmt: off
SECRET_TOO_SHORT_ERROR: Final[str] = (
    f"Secret is too short (minimum length: {SECRET_MINIMUM_LENGTH})"
)
SECRET_WITH_INVALID_CHARACTERS_ERROR: Final[str] = (
    "Secret contains invalid characters (only ASCII printable characters are allowed)"
)
MISSING_SECRET_ERROR: Final[str] = (
    "Secret field is required"
)
INCORRECT_SECRET_ERROR: Final[str] = (
    "Invalid secret for given note"
)
CONTENT_TOO_LONG_ERROR: Final[str] = (
    f"Content is too long (maximum length: {CONTENT_MAXIMUM_LENGTH})"
)
EXPIRATION_DATE_INVALID_FORMAT_ERROR: Final[str] = (
    f"Expiration date has invalid format (expected: {DATE_FORMAT.replace('%', '')!r})"
)
EXPIRATION_DATE_ALREADY_EXPIRED_ERROR: Final[str] = (
    "Expiration date is already expired"
)
# fmt: on


def date_expired(
    date: datetime.datetime,
    /,
    *,
    current_date: datetime.datetime = None,
) -> bool:
    """
    Verifies date expiration date. Returns True
    only if the date is less than current date.

    If `current_date` is not provided by the user,
    function calculates current date at the start.

    :param date: date to be verified
    :param current_date: date used to verify expiration date
    """

    current_date = current_date or datetime.datetime.now()

    return date < current_date


class Printable:

    """
    Validates that data contains printable string.
    """

    __slots__ = ("message",)

    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form: Form, field: Field, message: Optional[str] = None) -> None:
        if not all(character in string.printable for character in field.data or ""):
            raise ValidationError(message or self.message)


class NotExpired:

    """
    Validates that data contains date that did not expired.
    """

    __slots__ = ("message",)

    def __init__(self, message: str) -> None:
        self.message = message

    def __call__(self, form: Form, field: Field, message: Optional[str] = None) -> None:
        if date_expired(field.data):
            raise ValidationError(message or self.message)


class CreateNoteForm(Form):

    """
    Form for creating the note.
    """

    secret = PasswordField(
        "Secret",
        [
            validators.Length(min=SECRET_MINIMUM_LENGTH, message=SECRET_TOO_SHORT_ERROR),
            Printable(message=SECRET_WITH_INVALID_CHARACTERS_ERROR),
        ],
    )

    content = TextAreaField(
        "Content",
        [
            validators.Length(max=CONTENT_MAXIMUM_LENGTH, message=CONTENT_TOO_LONG_ERROR),
        ],
    )

    expiration_date = DateTimeField(
        "Expire",
        [
            validators.DataRequired(message=EXPIRATION_DATE_INVALID_FORMAT_ERROR),
            NotExpired(message=EXPIRATION_DATE_ALREADY_EXPIRED_ERROR),
        ],
        format=DATE_FORMAT,
    )


class AccessNoteForm(Form):

    """
    Form for accessing the note.
    """

    secret = PasswordField(
        "Secret",
        [
            validators.DataRequired(message=MISSING_SECRET_ERROR),
        ],
    )
