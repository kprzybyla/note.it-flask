__all__ = [
    "valid_secret",
    "valid_content",
    "valid_expiration_date",
    "build_create_data",
    "build_access_data",
    "extract_uid",
    "contains_once",
    "sleep_until",
    "INDEX_ROUTE",
    "HTML_CONTENT_TYPE",
    "UUID_VERSION",
    "SECRET_MINIMUM_LENGTH",
    "CONTENT_MAXIMUM_LENGTH",
    "DATE_FORMAT",
]

import time
import random
import string
import datetime

from typing import Union, Optional, Final

SLASH: Final[str] = "/"

INDEX_ROUTE: Final[str] = "/"
HTML_CONTENT_TYPE: Final[str] = "html/text"

SECRET_FIELD_NAME: Final[str] = "secret"
CONTENT_FIELD_NAME: Final[str] = "content"
EXPIRATION_DATE_FILED_NAME: Final[str] = "expiration_date"

UUID_VERSION: Final[int] = 4

SECRET_MINIMUM_LENGTH: Final[int] = 8
CONTENT_MAXIMUM_LENGTH: Final[int] = 500

DATE_FORMAT: Final[str] = "%d-%m-%Y, %H:%M:%S"


def valid_secret() -> str:
    length = random.randrange(SECRET_MINIMUM_LENGTH, 100)
    characters = random.choices(string.printable, k=length)

    return "".join(characters)


def valid_content() -> str:
    length = random.randrange(0, CONTENT_MAXIMUM_LENGTH)
    characters = random.choices(string.printable, k=length)

    return "".join(characters)


def valid_expiration_date() -> datetime.datetime:
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)

    return now + delta


def build_create_data(
    *,
    secret: Optional[str] = None,
    content: Optional[str] = None,
    expiration_date: Optional[Union[str, datetime.datetime]] = None,
) -> dict[str, str]:
    data: dict[str, str] = {}

    if secret is not None:
        data[SECRET_FIELD_NAME] = secret

    if content is not None:
        data[CONTENT_FIELD_NAME] = content

    if expiration_date is not None:
        if isinstance(expiration_date, str):
            data[EXPIRATION_DATE_FILED_NAME] = expiration_date
        else:
            data[EXPIRATION_DATE_FILED_NAME] = expiration_date.strftime(DATE_FORMAT)

    return data


def build_access_data(*, secret: Optional[str] = None) -> dict[str, str]:
    data: dict[str, str] = {}

    if secret is not None:
        data[SECRET_FIELD_NAME] = secret

    return data


def extract_uid(url: str, /) -> str:
    return url.strip(SLASH)


def contains_once(content: str, /, *, contains: str) -> bool:
    return content.count(contains) == 1


def sleep_until(date: datetime.datetime, /) -> None:
    now = datetime.datetime.now()
    amount = (date - now).total_seconds()

    time.sleep(amount)
