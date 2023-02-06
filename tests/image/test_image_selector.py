import re
import typing

import pytest

import bollard.image.selector as t


@pytest.mark.parametrize(
    ("selector", "result"),
    [
        # name
        ("name", True),
        ("sample", True),
        ("foo", False),
        # tag
        (":2023.2.0", True),
        (":2023*", True),
        (":*2023", False),
        # hex
        ("0000", True),  # id
        ("dddd", True),  # digest
        ("ffff", False),
        # repo
        ("example.com", True),
        ("example.com/sample", True),
        ("*/sample", True),
        ("example.com/name", False),
        # tag
        ("name:2023.2.0", True),
        ("sample:2023.2.0-foo", True),
        ("name:2023.2.0-foo", False),
        ("name:2023.2.0*", True),
    ],
)
def test_is_image_match_selector(selector: str, result: bool):
    data = {
        "Id": "sha256:00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "RepoTags": [
            "name:2023.2.0",
            "example.com/sample:2023.2.0-foo",
        ],
        "RepoDigests": [
            "name@sha256:ddddddddeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            "example.com/sample@sha256:22222222dddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        ],
    }
    assert t.is_image_match_selector(data, selector) is result


@pytest.mark.parametrize(
    ("selector", "expected_keys"),
    [
        # name
        ("NAME", ["NAME", "REGISTRY"]),
        ("*name", ["NAME", "REGISTRY", "REPO"]),
        ("name*", ["NAME", "REGISTRY", "REPO"]),
        ("example.com", ["NAME", "REGISTRY"]),
        # tag
        (":tag", ["TAG"]),
        (":*tag", ["TAG"]),
        (":tag*", ["TAG"]),
        # hex - and still possible to be name
        ("ffffff", ["ID", "DIGEST", "NAME", "REGISTRY"]),
        ("sha256:ffffff", ["ID", "DIGEST", "REPO_TAG"]),
        # registry + name
        ("example.com/name", ["REPO"]),
        ("*/name", ["REPO"]),
        ("example.com/*", ["REPO"]),
        # name + tag
        ("name:tag", ["REPO_TAG"]),
        ("*:tag", ["REPO_TAG"]),
        ("name:*", ["REPO_TAG"]),
        ("example.com/name:tag", ["REPO_TAG"]),
        ("*/name:tag", ["REPO_TAG"]),
        ("example.com/*:tag", ["REPO_TAG"]),
        ("example.com/name:*", ["REPO_TAG"]),
    ],
)
def test_translate_selector(selector: str, expected_keys: list[str]):
    output = {k: v for k, v in t.translate_selector(selector)}
    assert set(expected_keys) == set(output)
    assert all(isinstance(v, typing.Pattern) for v in output.values())


@pytest.mark.parametrize(
    ("selector"),
    [
        "-name",
        ":-tag",
    ],
)
def test_translate_selector_fail(selector: str, caplog: pytest.LogCaptureFixture):
    assert t.translate_selector(selector) == []
    assert re.search(r"Selector '.+' is not a valid pattern", caplog.text)
