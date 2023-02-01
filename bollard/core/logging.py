import functools
import logging
import sys

import click

STYLES = {
    "DEBUG": {"fg": "white", "bold": True},
    "INFO": {"fg": "green", "bold": True},
    "WARNING": {"fg": "yellow", "bold": True},
    "ERROR": {"fg": "red", "bold": True},
    "CRITICAL": {"fg": "white", "bg": "red", "bold": True},
}


class BollardHandler(logging.Handler):
    """Send the logs to click's echo."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            self.handleError(record)
            return
        click.echo(msg, file=sys.stderr)


@functools.cache
def get_level_prefix(level: str):
    text = f"[{level}]"
    style = STYLES[level]
    return click.style(text, **style)


class BollardFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level = get_level_prefix(record.levelname)

        name, *_ = record.name.split(".", 1)
        name = click.style(f"{name}:", fg="cyan")

        msg = super().format(record)

        return f"{level} {name} {msg}"


def setup_logger(level: int) -> None:
    h = BollardHandler()
    h.setFormatter(BollardFormatter())

    logging.root.setLevel(level)
    logging.root.addHandler(h)
