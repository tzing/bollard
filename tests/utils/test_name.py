import bollard.utils.name as t


def test_split_repo_tag():
    assert t.split_repo_tag("foo:bar") == ("", "foo", "bar")
    assert t.split_repo_tag("example.com/foo:bar") == ("example.com", "foo", "bar")
