__all__ = ["home", "view"]

import datetime

from http import HTTPStatus
from typing import Optional

import flask

from .model import db, Note
from .extras import HTTPMethod

from .forms import (
    date_expired,
    CreateNoteForm,
    AccessNoteForm,
    DATE_FORMAT,
    INCORRECT_SECRET_ERROR,
)


def home() -> str:
    """
    Index route for creating notes.
    """

    form = CreateNoteForm(flask.request.form)
    method = HTTPMethod(flask.request.method)

    if method is HTTPMethod.GET:
        return render_create_note(form)

    if method is HTTPMethod.POST:
        if not form.validate():
            return render_create_note(form)

        secret = form.secret.data
        content = form.content.data
        expiration = form.expiration_date.data

        note = Note(secret, content, expiration)

        db.session.add(note)
        db.session.commit()

        return flask.redirect(note.uid)

    raise NotImplementedError()  # pragma: no cover


def view(uid: str) -> str:
    """
    View route for viewing note with given UUID.

    :param uid: note UUID to be viewed
    """

    note = fetch_note_by_uid(uid)

    if note is None:
        return flask.abort(HTTPStatus.NOT_FOUND)

    expiration_date = note.expiration_date

    if date_expired(expiration_date):
        return render_note_expired(uid, expiration_date)

    form = AccessNoteForm(flask.request.form)
    method = HTTPMethod(flask.request.method)

    if method is HTTPMethod.GET:
        return render_access_note(form)

    if method is HTTPMethod.POST:
        if not form.validate():
            return render_access_note(form)

        secret = form.secret.data

        if not note.verify_secret(secret):
            flask.flash(INCORRECT_SECRET_ERROR)
            return render_access_note(form)

        return render_view_note(note)

    raise NotImplementedError()  # pragma: no cover


def fetch_note_by_uid(uid: str) -> Optional[Note]:
    """
    Returns :class:`Note` note that matches given UUID.

    :param uid: searched note UUID
    """

    return db.session.query(Note).filter_by(uid=uid).one_or_none()


def render_create_note(form: CreateNoteForm, /) -> str:
    """
    Renders `Create Note` view.

    :param form: an instance of :class:`CreateNoteForm`
    """

    return flask.render_template("note_create.html", form=form)


def render_access_note(form: AccessNoteForm, /) -> str:
    """
    Renders `Access Note` view.

    :param form: an instance of :class:`AccessNoteForm`
    """

    return flask.render_template("note_access.html", form=form)


def render_view_note(note: Note, /) -> str:
    """
    Renders `View Note` view.

    :param note: an instance of :class:`Note` to be viewed
    """

    return flask.render_template("note_view.html", note=note)


def render_note_expired(uid: str, expiration_date: datetime.datetime, /) -> str:
    """
    Renders `Note Expired` view.

    :param uid: note UUID
    :param expiration_date: expiration date
    """

    return flask.render_template(
        "note_expired.html",
        uid=uid,
        expiration_date=expiration_date.strftime(DATE_FORMAT),
    )
