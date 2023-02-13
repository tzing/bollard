import pytest

import bollard.image.display as t


def test_print_table(capsys: pytest.CaptureFixture):
    # success
    t.print_table(
        ["name", "id"],
        [
            {"name": "foo", "id": "aaaa"},
            {"id": "bbbb", "name": "bar"},
        ],
    )

    captured = capsys.readouterr()
    assert "NAME    ID" in captured.out
    assert "foo     aaaa" in captured.out
    assert "bar     bbbb" in captured.out


def test_print_table_1(capsys: pytest.CaptureFixture):
    t.print_table(["name"], [])
    captured = capsys.readouterr()
    assert "No data selected" in captured.out
