import os
import re

import pytest

import bollard.misc as t


def test_version(runner):
    rv = runner.invoke(t.version)

    regex_version = re.compile(r"Version: +\d+\.\d+\.\d+")

    idx_client = rv.output.find("Client:")
    assert regex_version.search(rv.output, idx_client)

    idx_bollard = rv.output.find("Bollard:")
    assert regex_version.search(rv.output, idx_bollard, idx_client)


@pytest.mark.skipif(
    os.getenv("CI") is not None, reason="Gh action runs sh, which is not supported"
)
def test_completion(runner):
    rv = runner.invoke(t.completion)
    assert rv.exit_code == 0
    assert "_bollard_completion" in rv.output
