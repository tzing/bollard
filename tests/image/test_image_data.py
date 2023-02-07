import re
from unittest.mock import patch

import click
import freezegun
import pytest

import bollard.image.data as t


def test_list_image_ids():
    for image_id in t.list_image_ids():
        assert isinstance(image_id, str)
        assert re.fullmatch("sha256:[0-9a-f]{64}", image_id)


def test_inspect_image(caplog: pytest.LogCaptureFixture):
    with (
        patch.object(
            t,
            "check_docker_output",
            return_value="""[
                {
                    "Id": "sha256:ffffffff"
                },
                {
                    "Id": "sha256:eeeeeeee"
                }
            ]""",
        ) as chk,
        patch.object(t, "__cache_image_data", {}),
    ):
        # query, mssing 1 output
        assert t.inspect_image(
            ["sha256:ffffffff", "sha256:eeeeeeee", "sha256:dddddddd"]
        ) == [
            {"Id": "sha256:ffffffff"},
            {"Id": "sha256:eeeeeeee"},
        ]

        # use cache
        assert t.inspect_image(["sha256:ffffffff"]) == [{"Id": "sha256:ffffffff"}]

    # check call count - the second call should not fire subprocess
    assert chk.call_count == 1

    # check warning
    assert "No such image: sha256:dddddddd" in caplog.text


@pytest.fixture()
def _patch_inspect(monkeypatch: pytest.MonkeyPatch):
    def mock_inspect(ids: list[str]):
        if "sha256:aaaa" in ids:
            yield {
                "Id": "sha256:aaaa",
                "Created": "2023-04-05T06:07:05.910Z",
                "RepoDigests": ["example.com/name@sha256:bbbb"],
                "RepoTags": ["name:latest", "example.com/foo:2023.2.0"],
                "Size": 1234,
                "Architecture": "arm64",
                "Os": "linux",
            }

    monkeypatch.setattr("bollard.image.data.inspect_image", mock_inspect)

    with freezegun.freeze_time("2023-4-5 06:07:08.910", tz_offset=8):
        yield


@pytest.mark.parametrize(
    ("column", "output"),
    [
        ("architecture", ["arm64"]),
        ("created:iso", ["2023-04-05T14:07:05+08:00"]),
        ("created", ["3 seconds ago"]),
        ("digest", ["bbbb"]),
        ("id", ["aaaa"]),
        ("name", ["name", "foo"]),
        ("os", ["linux"]),
        ("platform", ["linux/arm64"]),
        ("registry", ["", "example.com"]),
        ("repo_tag", ["name:latest", "example.com/foo:2023.2.0"]),
        ("repository", ["name", "example.com/foo"]),
        ("size", ["1.2 kB"]),
        ("tag", ["latest", "2023.2.0"]),
    ],
)
@pytest.mark.usefixtures("_patch_inspect")
def test_get_field_data(column: str, output: list):
    assert list(t.get_field_data("sha256:aaaa", column, {})) == output


def test_format_architecture(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("platform.machine", lambda: "amd64")

    assert t.format_architecture("amd64", {}) == "amd64"
    assert t.format_architecture("test", {"highlight_architecture": False}) == "test"

    colored = click.style("test", fg="yellow", bold=True)
    assert t.format_architecture("test", {}) == colored