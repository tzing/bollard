from unittest.mock import patch

import bollard.image.rm as t


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
