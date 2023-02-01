import functools
import logging
import typing
from typing import Optional, Sequence

import click

if typing.TYPE_CHECKING:
    from subprocess import CompletedProcess


logger = logging.getLogger(__name__)


@functools.cache
def get_command_path(name: str) -> str | None:
    """Get path to the command. Returns None when not installed."""
    import subprocess

    # query
    # https://pubs.opengroup.org/onlinepubs/9699919799/utilities/command.html
    rv = subprocess.run(
        ["command", "-v", name], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    if rv.returncode != 0:
        # fail
        return None

    # success
    path = rv.stdout.rstrip().decode()
    return path


@functools.cache
def is_docker_daemon_running() -> bool:
    """Check if dockerd is running."""
    import socket

    from bollard.constants import pkg_version

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        try:
            # https://docs.docker.com/engine/api/v1.18/#1-brief-introduction
            s.connect("/var/run/docker.sock")

            # https://docs.docker.com/engine/api/v1.18/#ping-the-docker-server
            request = b"\r\n".join(
                [
                    b"GET /_ping HTTP/1.1",
                    b"Host: localhost",
                    b"User-Agent: bollard/" + pkg_version.encode(),
                    b"Accept: text/plain",
                    b"",
                    b"",
                ]
            )
            s.sendall(request)

            response = s.recv(64)

        except socket.error:
            return False

    if response:
        # response should be like:
        #   HTTP/1.1 200 OK
        #   ...
        _, code, _ = response.split(maxsplit=2)
        if code == b"200":
            return True

    return False


@functools.cache
def is_docker_ready() -> bool:
    if not get_command_path("docker"):
        logger.warning("Command not found: %s", "docker")
        return False

    if not is_docker_daemon_running():
        logger.warning("Docker daemon is not running")
        return False

    return True


def run_docker(
    args: Sequence[str],
    *,
    use_context: bool = True,
    stdout=None,
    stderr=None,
) -> Optional["CompletedProcess"]:
    """A :func:`subprocess.run` to run docker commands, with some functional
    check before the command runs."""
    import subprocess

    if not is_docker_ready():
        return None

    cmd = [get_command_path("docker")]

    if use_context:
        ctx = click.globals.get_current_context()
        cmd += ctx.meta.get("DOCKER_GLOBAL_OPTION", [])

    cmd += list(args)

    logger.debug("Invoke docker command: %s", cmd)
    return subprocess.run(cmd, stdout=stdout, stderr=stderr)


def check_docker_output(args: Sequence[str], *, use_context: bool = True) -> bytes:
    """A :func:`subprocess.check_output` to run docker command and returns its
    output, with some functional check before the command runs."""
    import subprocess

    if rv := run_docker(
        args, use_context=use_context, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    ):
        return rv.stdout

    return b""
