import click

from bollard.constants import pkg_version
from bollard.core import main
from bollard.utils import check_docker_output


@main.command()
def version():
    """Print version information"""
    click.echo("Bollard:")
    click.echo(f" Version:           {pkg_version}")

    if docker_version_info := check_docker_output(["version"], use_context=False):
        click.echo()
        click.echo(docker_version_info)


@main.command()
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish"], False),
    required=False,
)
@click.pass_context
def completion(ctx: click.Context, shell: str):
    """Print shell completion source script

    Click provides tab completion support, which need to invoked with a special
    environment variable. This command is a shortcut to get the completion script.
    """
    if not shell:
        import os

        shell_var = os.getenv("SHELL", "")
        shell = os.path.basename(shell_var)

    if not shell:
        ctx.fail("shell type unknown")

    from click.shell_completion import shell_complete

    shell_complete(
        main,
        {},
        "bollard",
        "_BOLLARD_COMPLETE",
        f"{shell}_source",
    )
