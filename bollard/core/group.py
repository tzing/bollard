import logging
import sys
import typing

import click

from bollard.utils import run_docker

if typing.TYPE_CHECKING:
    from click import Command, Context

BASE_COMMAND = "docker"

logger = logging.getLogger(__name__)


class BollardGroup(click.Group):
    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, "Command"] | list["Command"] | None = None,
        **attrs,
    ) -> None:
        super().__init__(name, commands, **attrs)
        self.aliases = {}

    def resolve_command(
        self, ctx: "Context", args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Invokes wrapped function when implemented, and fallback to docker
        when no match."""
        cmd_name = click.utils.make_str(args[0])

        # return the command's name, in case it is alias
        if cmd := self.get_command(ctx, cmd_name):
            return cmd.name, cmd, args[1:]

        # check alias table
        if alias := self.aliases.get(cmd_name):
            args_extended = list(alias) + args[1:]
            return self.resolve_command(ctx, args_extended)

        # command name does not match any implemented wrapper, pass args to docker
        return cmd_name, create_phony_command(), args[1:]

    def create_phony_command(self, name: str, doc: str) -> "Command":
        """Register a fake command in this group. This command forwards parameters
        to docker cli on invoke."""
        cmd = create_phony_command(name, doc)
        self.add_command(cmd)
        return cmd

    def add_unwrapped_targets(self, targets: list[tuple[str, str]]) -> None:
        """Add unwrapped targets as a fake command in this group. For displaying
        commands and its description in help text."""
        for cmd, desc in targets:
            if cmd not in self.commands:
                self.create_phony_command(cmd, desc)


def create_phony_command(name: str | None = None, help: str | None = None) -> "Command":
    """Create a command object that forwards parameters to docker cli."""

    @click.pass_context
    def invoke_docker(ctx: "Context"):
        args = ctx.command_path.split()[1:]
        args += ctx.args

        rv = run_docker(args)
        sys.exit(rv.returncode)

    return click.Command(
        name=name,
        context_settings={
            "allow_extra_args": True,
            "help_option_names": [],
            "ignore_unknown_options": True,
        },
        callback=invoke_docker,
        help=help,
    )
