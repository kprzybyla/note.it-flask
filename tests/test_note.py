import html
import uuid
import base64
import string
import datetime
import urllib.parse

from http import HTTPStatus
from typing import Final

import pytest

from flask import request, Response
from flask.testing import FlaskClient
from hypothesis import assume, given, settings, strategies as st

from .helpers import (
    valid_secret,
    valid_content,
    valid_expiration_date,
    build_create_data,
    build_access_data,
    extract_uid,
    contains_once,
    sleep_until,
    INDEX_ROUTE,
    HTML_CONTENT_TYPE,
    UUID_VERSION,
    SECRET_MINIMUM_LENGTH,
    CONTENT_MAXIMUM_LENGTH,
    DATE_FORMAT,
)

# fmt: off
NOTE_CREATE_INFO: Final[str] = (
    "Create note"
)
NOTE_ACCESS_INFO: Final[str] = (
    "Access note"
)
NOTE_CREATE_SECRET_TOO_SHORT_ERROR: Final[str] = (
    f"Secret is too short (minimum length: {SECRET_MINIMUM_LENGTH})"
)
NOTE_CREATE_SECRET_WITH_INVALID_CHARACTERS_ERROR: Final[str] = (
    "Secret contains invalid characters (only ASCII printable characters are allowed)"
)
NOTE_CREATE_CONTENT_TOO_LONG_ERROR: Final[str] = (
    f"Content is too long (maximum length: {CONTENT_MAXIMUM_LENGTH})"
)
NOTE_CREATE_EXPIRATION_DATE_INVALID_FORMAT_ERROR: Final[str] = (
    f"Expiration date has invalid format (expected: {DATE_FORMAT.replace('%', '')!r})"
)
NOTE_CREATE_EXPIRATION_DATE_ALREADY_EXPIRED_ERROR: Final[str] = (
    "Expiration date is already expired"
)
NOTE_ACCESS_MISSING_SECRET_ERROR: Final[str] = (
    "Secret field is required"
)
NOTE_ACCESS_INVALID_SECRET_ERROR: Final[str] = (
    "Invalid secret for given note"
)
NOTE_ACCESS_EXPIRED_ERROR: Final[str] = (
    'Note with UID "{uid}" expired at {date}'
)
# fmt: on


def test_index_success(tester: FlaskClient) -> None:
    response: Response = tester.get(INDEX_ROUTE, content_type=HTML_CONTENT_TYPE)

    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    info = NOTE_CREATE_INFO

    assert contains_once(page_data, contains=info), page_data


@pytest.mark.parametrize("method", ["PUT", "DELETE", "CONNECT", "TRACE", "PATCH"])
def test_index_failure_method_not_allowed(tester: FlaskClient, method: str) -> None:
    response: Response = tester.open(method=method)

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_create_note_success(tester: FlaskClient) -> None:
    data = build_create_data(
        secret=valid_secret(),
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path != INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    info = NOTE_ACCESS_INFO

    assert contains_once(page_data, contains=info), page_data

    uid = extract_uid(request.path)
    uuid_bytes = base64.urlsafe_b64decode(uid)
    uuid_object = uuid.UUID(bytes=uuid_bytes)

    assert isinstance(uuid_object, uuid.UUID)
    assert uuid_object.version == UUID_VERSION


def test_create_note_failure_missing_secret(tester: FlaskClient) -> None:
    data = build_create_data(
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_SECRET_TOO_SHORT_ERROR

    assert contains_once(page_data, contains=error), page_data


def test_create_note_failure_missing_expiration_date(tester: FlaskClient) -> None:
    data = build_create_data(
        secret=valid_secret(),
        content=valid_content(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_EXPIRATION_DATE_INVALID_FORMAT_ERROR

    assert contains_once(page_data, contains=error), page_data


@given(
    secret=st.text(
        alphabet=string.printable,
        max_size=SECRET_MINIMUM_LENGTH - 1,
    )
)
def test_create_note_failure_secret_too_short(tester: FlaskClient, secret: str) -> None:
    data = build_create_data(
        secret=secret,
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_SECRET_TOO_SHORT_ERROR

    assert contains_once(page_data, contains=error), page_data


@given(
    secret=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs",),
            blacklist_characters=string.printable,
        ),
        min_size=SECRET_MINIMUM_LENGTH,
    )
)
def test_create_note_failure_secret_with_invalid_characters(
    tester: FlaskClient,
    secret: str,
) -> None:
    data = build_create_data(
        secret=secret,
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_SECRET_WITH_INVALID_CHARACTERS_ERROR

    assert contains_once(page_data, contains=error), page_data


@settings(max_examples=10)
@given(
    content=st.text(
        min_size=CONTENT_MAXIMUM_LENGTH + 1,
    )
)
def test_create_note_failure_content_too_long(tester: FlaskClient, content: str) -> None:
    data = build_create_data(
        secret=valid_secret(),
        content=content,
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_CONTENT_TOO_LONG_ERROR

    assert contains_once(page_data, contains=error), page_data


@given(expiration_date=st.datetimes())
@pytest.mark.parametrize(
    "date_format",
    [
        "%d-%m-%Y, %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%H:%M:%S, %d-%m-%Y",
        "%d/%m/%Y, %H:%M:%S",
    ],
)
def test_create_note_failure_expiration_date_invalid_format(
    tester: FlaskClient,
    expiration_date: datetime.datetime,
    date_format: str,
) -> None:
    data = build_create_data(
        secret=valid_secret(),
        content=valid_content(),
        expiration_date=expiration_date.strftime(date_format),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_EXPIRATION_DATE_INVALID_FORMAT_ERROR

    assert contains_once(page_data, contains=error), page_data


def test_create_note_failure_expiration_date_already_expired(tester: FlaskClient) -> None:
    data = build_create_data(
        secret=valid_secret(),
        content=valid_content(),
        expiration_date=datetime.datetime.now(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path == INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_CREATE_EXPIRATION_DATE_ALREADY_EXPIRED_ERROR

    assert contains_once(page_data, contains=error), page_data


def test_access_note_success(tester: FlaskClient) -> None:
    secret = valid_secret()
    content = valid_content()

    data = build_create_data(
        secret=secret,
        content=content,
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path != INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())

    assert contains_once(page_data, contains=NOTE_ACCESS_INFO), page_data

    url = request.path
    data = build_access_data(secret=secret)

    response: Response = tester.post(url, data=data)

    assert request.path == url
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())

    assert contains_once(page_data, contains=content), page_data


@given(text=st.binary(min_size=1))
def test_access_note_failure_invalid_uid(tester: FlaskClient, text: str) -> None:
    uid = base64.urlsafe_b64encode(text).decode()
    url = urllib.parse.urljoin(INDEX_ROUTE, uid)

    response: Response = tester.get(url, content_type=HTML_CONTENT_TYPE)

    assert response.status_code == HTTPStatus.NOT_FOUND


@given(
    secret=st.text(
        alphabet=string.printable,
        min_size=SECRET_MINIMUM_LENGTH,
    )
)
def test_access_note_failure_missing_secret(
    tester: FlaskClient,
    secret: str,
) -> None:
    data = build_create_data(
        secret=secret,
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path != INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())

    assert contains_once(page_data, contains=NOTE_ACCESS_INFO), page_data

    url = request.path
    data = build_access_data()

    response: Response = tester.post(url, data=data)

    assert request.path == url
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_ACCESS_MISSING_SECRET_ERROR

    assert contains_once(page_data, contains=error), page_data


@given(
    secret=st.text(
        alphabet=string.printable,
        min_size=SECRET_MINIMUM_LENGTH,
    ),
    invalid_secret=st.text(
        alphabet=string.printable,
        min_size=1,
    ),
)
def test_access_note_failure_invalid_secret(
    tester: FlaskClient,
    secret: str,
    invalid_secret: str,
) -> None:
    assume(secret.strip())
    assume(invalid_secret.strip())
    assume(secret != invalid_secret)

    data = build_create_data(
        secret=secret,
        content=valid_content(),
        expiration_date=valid_expiration_date(),
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path != INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())

    assert contains_once(page_data, contains=NOTE_ACCESS_INFO), page_data

    url = request.path
    data = build_access_data(secret=invalid_secret)

    response: Response = tester.post(url, data=data)

    assert request.path == url
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_ACCESS_INVALID_SECRET_ERROR

    assert contains_once(page_data, contains=error), page_data


def test_access_note_failure_expired(tester: FlaskClient) -> None:
    secret = valid_secret()
    expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=1)

    data = build_create_data(
        secret=secret,
        content=valid_content(),
        expiration_date=expiration_date,
    )

    response: Response = tester.post(INDEX_ROUTE, data=data, follow_redirects=True)

    assert request.path != INDEX_ROUTE
    assert response.status_code == HTTPStatus.OK

    sleep_until(expiration_date)

    page_data = html.unescape(response.data.decode())

    assert contains_once(page_data, contains=NOTE_ACCESS_INFO), page_data

    url = request.path
    data = build_access_data(secret=secret)

    response: Response = tester.post(url, data=data)

    assert request.path == url
    assert response.status_code == HTTPStatus.OK

    page_data = html.unescape(response.data.decode())
    error = NOTE_ACCESS_EXPIRED_ERROR.format(
        uid=extract_uid(url),
        date=expiration_date.strftime(DATE_FORMAT),
    )

    assert contains_once(page_data, contains=error), page_data
