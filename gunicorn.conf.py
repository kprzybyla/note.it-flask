import multiprocessing

from typing import Final
from dataclasses import dataclass, field

_WORKERS_PER_CORE: Final[int] = 2


def _workers() -> int:
    return multiprocessing.cpu_count() * _WORKERS_PER_CORE


@dataclass
class _Config:

    bind: str = field(default="0.0.0.0:80")
    workers: int = field(default_factory=_workers)
    loglevel: str = field(default="info")
    keepalive: int = field(default=120)
    errorlog: str = field(default="-")


_config = _Config()

""" GUNICORN CONFIG """

loglevel = _config.loglevel
workers = _config.workers
bind = _config.bind
keepalive = _config.keepalive
errorlog = _config.errorlog
