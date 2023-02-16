import datetime
import os
import re
import zoneinfo

import freezegun

import bollard.utils.format as t


def test_format_iso_time():
    t0 = datetime.datetime(
        2021, 2, 3, 4, 5, 6, tzinfo=zoneinfo.ZoneInfo("Europe/Zurich")
    )
    tf = t.format_iso_time(t0)

    assert re.fullmatch(r"2021-02-0[23]T\d{2}:05:06[+-]\d{2}:\d{2}", tf)

    if os.getenv("CI"):  # gh server is utc, shift -1 from t0
        assert tf == "2021-02-03T03:05:06+00:00"


@freezegun.freeze_time("2023-4-5 06:07:08.910", tz_offset=8)
def test_format_relative_time():
    assert t.format_relative_time("2023-04-05T06:07:05.910Z") == "3 seconds ago"
    assert t.format_relative_time("2023-01-01T00:00:00.000Z") == "3 months ago"


def test_format_digest():
    digest = "sha256:1234567890ffffffffff1234567890ffffffffff1234567890ffffffffff1234"
    assert t.format_digest(digest, True) == "1234567890ff"
    assert t.format_digest(digest, False) == digest


def test_format_size():
    assert t.format_size(1234) == "1.2 kB"
