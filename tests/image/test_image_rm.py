from unittest.mock import patch

import click.testing

import bollard.image.rm as t


def test_cli(runner: click.testing.CliRunner):
    # empty
    rv = runner.invoke(t.remove_images, ["no-this-image"])
    assert "No image to be removed" in rv.output
    assert rv.exit_code == 1

    # removed
    with (
        patch.object(t, "select_images", return_value=["aaaa"]),
        patch.object(t, "run_docker") as dkr,
        patch("bollard.image.data.collect_fields"),
        patch("bollard.image.display.print_table"),
    ):
        rv = runner.invoke(t.remove_images, ["-fy", "test"])
    assert rv.exit_code == 0
    dkr.assert_any_call(["image", "rm", "-f", "aaaa"])


def test_select_images():
    with (
        patch("bollard.image.data.list_image_ids"),
        patch(
            "bollard.image.data.inspect_image",
            return_value=[
                {"Id": "sha256:aaaa", "RepoTags": ["test:latest"]},
                {"Id": "sha256:bbbb", "RepoTags": ["foo:latest"]},
                {"Id": "sha256:cccc", "RepoTags": ["foo:2023.2.0"]},
            ],
        ),
    ):
        assert t.select_images(["aaaa"]) == ["sha256:aaaa"]
        assert t.select_images([":latest"]) == ["sha256:aaaa", "sha256:bbbb"]


def test_interactive_select_image():
    with (
        patch("bollard.image.data.list_image_ids"),
        patch(
            "bollard.image.data.collect_fields",
            return_value=[
                {
                    "id": "aaaa",
                    "size": "10 kB",
                    "created": "when",
                    "repo_tag": "foo:2023.2.0",
                },
                {
                    "id": "aaaa",
                    "size": "10 kB",
                    "created": "when",
                    "repo_tag": "bar:latest",
                },
            ],
        ),
        patch(
            "bollard.utils.interactive_select", return_value=["aaaa ...", "aaaa ..."]
        ),
    ):
        assert t.interactive_select_image() == {"aaaa"}
