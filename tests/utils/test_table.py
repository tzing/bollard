import bollard.utils.table as t


def test_tabulate():
    data = [
        {"foo": "", "bar": "test"},
        {"bar": None, "foo": "test"},
    ]

    # success - just test for no error
    o = t.tabulate({"foo": None, "bar": {"title": "SAMPLE"}}, data)
    assert isinstance(o, str)

    o = t.tabulate(["foo", "bar"], data, False)
    assert isinstance(o, str)
    assert "foo" not in o

    # fail
    assert "No data selected" in t.tabulate({}, [])
