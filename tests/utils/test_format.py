import datetime

import bollard.utils.format as t


import freezegun


@freezegun.freeze_time("2023-4-5 06:07:08.910", tz_offset=8)
def test_format_iso_time():
    assert t.format_iso_time("2023-04-05T06:07:08.910Z") == "2023-04-05T14:07:08+08:00"
    assert t.format_iso_time(datetime.datetime.now()) == "2023-04-05T14:07:08+08:00"


@freezegun.freeze_time("2023-4-5 06:07:08.910", tz_offset=8)
def test_format_relative_time():
    assert t.format_relative_time("2023-04-05T06:07:05.910Z") == "3 seconds ago"
    assert t.format_relative_time("2023-01-01T00:00:00.000Z") == "3 months ago"


def test_format_digest():
    digest = "sha256:1234567890ffffffffff1234567890ffffffffff1234567890ffffffffff1234"
    assert (
        t.format_digest(digest, True)
        == "sha256:1234567890ffffffffff1234567890ffffffffff1234567890ffffffffff1234"
    )
    assert t.format_digest(digest, False) == "1234567890ff"


def test_format_size():
    assert t.format_size(1234) == "1.2 kB"
