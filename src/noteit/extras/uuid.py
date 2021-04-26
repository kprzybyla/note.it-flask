__all__ = ["UUID"]

import uuid
import base64

from typing import Final
from sqlalchemy import String

UUID_LENGTH: Final[int] = 24


class UUID(String):

    """
    The UUID column type.

    This class exists for compability reasons with dialects other than PostgreSQL.
    If the database backend relies purely on PostgreSQL, this can be replaced by:

    >>> from sqlalchemy.dialects.postgresql import UUID
    """

    __slots__ = ()

    def __init__(self):
        super().__init__(length=UUID_LENGTH)

    @staticmethod
    def random() -> str:

        """
        Function for generating random UUIDs.
        """

        uid = uuid.uuid4()
        uri = base64.urlsafe_b64encode(uid.bytes)

        return uri.decode()
