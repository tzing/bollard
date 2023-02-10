import bollard.utils.table as t


def test_build_table():
    data = [
        {"foo": "", "bar": "test"},
        {"bar": None, "foo": "test"},
    ]

    # success - just test for no error
    o = t.build_table({"foo": None, "bar": {"title": "SAMPLE"}}, data)
    assert isinstance(o, str)
    o = t.build_table(["foo", "bar"], data)
    assert isinstance(o, str)

    # fail
    assert "No data selected" in t.build_table({}, [])
