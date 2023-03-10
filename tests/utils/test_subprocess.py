import re
import subprocess
from unittest.mock import Mock

import click
import pytest

import bollard.utils.subprocess as t


def test_get_command_path():
    assert isinstance(t.get_command_path("bash"), str)
    assert t.get_command_path("no-this-command") is None


def test_is_docker_daemon_running():
    assert t.is_docker_daemon_running() is True


class TestIsDockerReady:
    def teardown_method(self):
        t.is_docker_ready.cache_clear()

    def test_success(self):
        assert t.is_docker_ready() is True

    def test_fail_1(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        monkeypatch.setattr(t, "get_command_path", lambda _: None)
        assert t.is_docker_ready() is False
        assert "Command 'docker' not found" in caplog.text

    def test_fail_2(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ):
        monkeypatch.setattr(t, "is_docker_daemon_running", lambda: False)
        assert t.is_docker_ready() is False
        assert "Docker daemon is not running" in caplog.text


@pytest.mark.usefixtures("_with_click_context")
def test_check_docker_output():
    assert re.match(
        rb"Docker version \d+\.\d+\.\d+", t.check_docker_output(["--version"])
    )


def test_check_docker_output_fail(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(t, "is_docker_ready", lambda: False)
    with pytest.raises(click.Abort):
        t.check_docker_output(["--version"])


def test_interactive_select(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(t, "get_command_path", lambda _: "/test/fzf")

    def mock_run(args, **kwargs):
        assert kwargs["input"] == b"aaa\nbbb\nccc"

        rv = Mock(spec=subprocess.CompletedProcess)
        rv.stdout = b"aaa\nbbb"
        return rv

    monkeypatch.setattr("subprocess.run", mock_run)

    assert t.interactive_select(
        ["aaa", "bbb", "ccc"],
        header="test header",
        prompt="test prompt",
    ) == ["aaa", "bbb"]

    assert t.interactive_select([]) == []


def test_interactive_select_fail(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(t, "get_command_path", lambda _: None)

    with pytest.raises(click.Abort):
        t.interactive_select(["aaa"])
