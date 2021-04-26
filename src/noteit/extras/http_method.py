__all__ = ["HTTPMethod"]

import enum


class HTTPMethod(enum.Enum):

    """
    Enum class for mapping HTTP Methods.
    """

    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"
