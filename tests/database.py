import time
import atexit
import contextlib

from typing import Final

import docker

from docker.errors import NotFound

DEFAULT_PORT: Final[int] = 5432
DOCKER_IMAGE: Final[str] = "postgres:13-alpine"
ACCEPTING_CONNECTIONS_EXIT_CODE: Final[int] = 0

client: Final = docker.from_env()


class Database:

    __slots__ = (
        "_container",
        "_database",
        "_host",
        "_port",
        "_username",
        "_password",
    )

    def __init__(
        self,
        database: str = "main",
        host: str = "127.0.0.1",
        port: int = 5550,
        username: str = "root",
        password: str = "root",
    ):
        self._database = database
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def __enter__(self) -> "Database":
        atexit.register(self.destroy)

        env = {
            "POSTGRES_DB": self._database,
            "POSTGRES_HOST": self._host,
            "POSTGRES_PORT": str(self._port),
            "POSTGRES_USER": self._username,
            "POSTGRES_PASSWORD": self._password,
        }

        ports = {
            f"{DEFAULT_PORT}/tcp": self._port,
        }

        self._container = client.containers.run(
            image=DOCKER_IMAGE,
            environment=env,
            ports=ports,
            detach=True,
        )

        self.wait_until_ready()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.destroy()

    @property
    def uri(self) -> str:
        location = f"{self._host}:{self._port}/{self._database}"
        credentials = f"{self._username}:{self._password}"

        return f"postgresql://{credentials}@{location}"

    def wait_until_ready(self) -> None:
        command = f"pg_isready -U {self._username} -d {self._database}"

        while True:
            result = self._container.exec_run(command)

            if result.exit_code != ACCEPTING_CONNECTIONS_EXIT_CODE:
                time.sleep(0.5)
            else:
                break

    def destroy(self) -> None:
        container = self._container

        with contextlib.suppress(NotFound):
            container.kill()
            container.remove()
