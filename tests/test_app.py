import os
import string
import contextlib

from hypothesis import given, strategies as st

from noteit.app import get_database_uri


@contextlib.contextmanager
def push_env() -> None:
    environ = os.environ.copy()
    yield
    os.environ = environ


@given(
    db=st.text(alphabet=string.printable, min_size=1),
    host=st.text(alphabet=string.printable, min_size=1),
    port=st.integers(max_value=0xFFFF),
    username=st.text(alphabet=string.printable, min_size=1),
    password=st.text(alphabet=string.printable, min_size=1),
)
def test_get_database_uri(
    db: str,
    host: str,
    port: int,
    username: str,
    password: str,
) -> None:
    expected = f"postgresql://{username}:{password}@{host}:{port}/{db}"

    with push_env():
        os.environ["POSTGRES_DB"] = db
        os.environ["POSTGRES_HOST"] = host
        os.environ["POSTGRES_PORT"] = str(port)
        os.environ["POSTGRES_USER"] = username
        os.environ["POSTGRES_PASSWORD"] = password

        assert get_database_uri() == expected
