import logging
import re
import typing

import click
import pytest

import bollard.core.group as t

if typing.TYPE_CHECKING:
    from click.testing import CliRunner


class TestBollardGroup:
    @pytest.fixture(scope="class")
    def bollardgroup(self):
        g = t.BollardGroup()

        # test case: implemented function
        @g.command
        def foo():
            click.echo("foo")

        # test case: alias
        g.aliases["bar"] = ["foo", "--help"]

        return g

    def test_resolve_command_implemented(self, bollardgroup, runner: "CliRunner"):
        rv = runner.invoke(bollardgroup, ["foo"])
        assert rv.exit_code == 0
        assert rv.stdout == "foo\n"

    def test_resolve_command_alias(self, bollardgroup, runner: "CliRunner"):
        rv = runner.invoke(bollardgroup, ["bar"])
        assert rv.exit_code == 0
        assert rv.stdout.startswith("Usage: root foo [OPTIONS]")

    def test_resolve_command_unwrapped(
        self, bollardgroup, runner: "CliRunner", caplog: pytest.LogCaptureFixture
    ):
        # unwrapped: should invoke docker
        with caplog.at_level(logging.DEBUG):
            rv = runner.invoke(bollardgroup, ["version", "--help"])
        assert rv.exit_code == 0
        assert re.search(
            r"Invoke docker command: \['.+/docker', 'version', '--help'\]", caplog.text
        )


def test_create_phony_command(runner: "CliRunner", caplog: pytest.LogCaptureFixture):
    cmd = t.create_phony_command("test", "sample docstring")

    # trigger `docker --version`
    with caplog.at_level(logging.DEBUG):
        runner.invoke(cmd, ["--version"])
    assert re.search(
        r"Invoke docker command: \['.+/docker', '--version'\]", caplog.text
    )
