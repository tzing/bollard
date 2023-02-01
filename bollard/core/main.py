import logging

import click

from bollard.core.group import BollardGroup
from bollard.core.logging import setup_logger
from bollard.utils import append_parameters, rebuild_args

# docker's global options that is not used by this main func
# built them to the main command object for better UX
DOCKER_OPTIONS = [
    click.Option(
        ["--config"],
        help="Location of client config files",
    ),
    click.Option(
        ["-c", "--context"],
        help="Name of the context to use to connect to the daemon "
        '(overrides DOCKER_HOST env var and default context set with "docker context use").',
    ),
    click.Option(
        ["-D", "--debug"],
        is_flag=True,
        help="Enable debug mode.",
    ),
    click.Option(
        ["-H", "--host"],
        multiple=True,
        help="Daemon socket(s) to connect to.",
    ),
    click.Option(
        ["-l", "--log-level"],
        type=click.Choice(["debug", "info", "warn", "error", "fatal"], False),
        help="Set the logging level.",
    ),
    click.Option(
        ["--tls"],
        is_flag=True,
        help="Use TLS; implied by --tlsverify.",
    ),
    click.Option(
        ["--tlscacert"],
        type=click.Path(True, dir_okay=False),
        help="Trust certs signed only by this CA.",
    ),
    click.Option(
        ["--tlscert"],
        type=click.Path(True, dir_okay=False),
        help="Path to TLS certificate file.",
    ),
    click.Option(
        ["--tlskey"],
        type=click.Path(True, dir_okay=False),
        help="Path to TLS key file.",
    ),
    click.Option(
        ["--tlsverify"],
        is_flag=True,
        help="Use TLS and verify the remote",
    ),
]

LEVEL_MAPPING = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
    "fatal": logging.CRITICAL,
}

logger = logging.getLogger(__name__)


@click.group(
    cls=BollardGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def main(ctx: click.Context, **extra):
    """Wrapper for docker command that provide handful options and alias."""
    # setup logger, use the value from --log-level
    log_level_raw = extra.get("log_level")
    log_level = LEVEL_MAPPING.get(log_level_raw, logging.INFO)

    setup_logger(log_level)

    # add docker's options to context
    docker_global_options = rebuild_args(extra, DOCKER_OPTIONS)
    if docker_global_options:
        ctx.meta["DOCKER_GLOBAL_OPTION"] = docker_global_options


append_parameters(main, DOCKER_OPTIONS)
