from unittest.mock import patch

import pytest

import bollard.image.ls as t


def test_get_columns():
    default = ["id", "repository", "tag", "created", "size"]
    assert t.get_columns([]) == default
    assert t.get_columns([], flag_format=True) == default

    default_and_digest = ["id", "repository", "tag", "created", "size", "digest"]
    assert t.get_columns([], flag_digest=True) == default_and_digest
    compact_and_digest = ["id", "repo_tag", "digest"]
    assert t.get_columns(["compact"], flag_digest=True) == compact_and_digest

    assert t.get_columns([], flag_quiet=True) == ["id"]
    assert t.get_columns([], flag_quiet=True, flag_digest=True) == ["id"]


def test_norm_columns():
    assert t.norm_columns(["default", "arch", "repo", "platform"]) == [
        "id",
        "repository",
        "tag",
        "created",
        "size",
        "architecture",
        "platform",
    ]


@pytest.mark.usefixtures("_with_click_context")
def test_list_images_fallback():
    with pytest.raises(SystemExit) as e:
        t.list_images_fallback({})
    assert e.value.code == 0


def test_select_images():
    with (
        patch(
            "bollard.image.data.list_image_ids",
            return_value=["sha256:aaaa", "sha256:bbbb", "sha256:cccc"],
        ),
        patch(
            "bollard.image.data.inspect_image",
            return_value=[
                {"Id": "sha256:aaaa", "RepoTags": ["test:latest"]},
                {"Id": "sha256:bbbb", "RepoTags": ["foo:latest"]},
                {"Id": "sha256:cccc", "RepoTags": ["foo:2023.2.0"]},
            ],
        ),
    ):
        assert t.select_images((), False, ("mocked",)) == [
            "sha256:aaaa",
            "sha256:bbbb",
            "sha256:cccc",
        ]
        assert t.select_images((":latest",), False, ()) == [
            "sha256:aaaa",
            "sha256:bbbb",
        ]


def test_parse_top_n_arg():
    assert t.parse_top_n_arg(["foo", "~3", "bar", "~1"]) == (["foo", "bar"], 1)


def test_order_dict():
    data = [
        {"foo": 10, "bar": 10},
        {"foo": 20, "bar": 20},
    ]
    assert t.order_dict(data, "foo", True) == [
        {"foo": 20, "bar": 20},
        {"foo": 10, "bar": 10},
    ]
    assert t.order_dict(data, "foo", False) == [
        {"foo": 10, "bar": 10},
        {"foo": 20, "bar": 20},
    ]
