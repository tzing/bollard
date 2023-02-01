import bollard.utils.params as t

import click


def test_rebuild_args():
    params = [
        click.Option(["--str"]),
        click.Option(["--flag"], is_flag=True),
        click.Option(["-m", "--multiple"], multiple=True),
    ]

    assert t.rebuild_args({"str": "test"}, params) == ["--str", "test"]
    assert t.rebuild_args({"flag": True}, params) == ["--flag"]
    assert t.rebuild_args({"flag": False}, params) == []
    assert t.rebuild_args({"multiple": (123, 456)}, params) == [
        "-m",
        "123",
        "-m",
        "456",
    ]
    assert t.rebuild_args({}, params) == []


def test_append_parameters(runner):
    cmd = click.Command("test")

    rv = runner.invoke(cmd, ["-t"])
    assert rv.exit_code != 0

    t.append_parameters(cmd, [click.Option(["-t", "--test"], is_flag=True)])
    rv = runner.invoke(cmd, ["-t"])
    assert rv.exit_code == 0
