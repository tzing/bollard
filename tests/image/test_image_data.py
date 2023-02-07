import re
from unittest.mock import patch

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
