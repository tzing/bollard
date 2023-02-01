import click.testing
import pytest


@pytest.fixture()
def _with_click_context():
    with click.Context(click.Command("test")):
        yield


@pytest.fixture()
def runner() -> click.testing.CliRunner:
    return click.testing.CliRunner()
