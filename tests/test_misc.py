import re

import bollard.misc as t


def test_version(runner):
    rv = runner.invoke(t.version)
    assert re.search(PATTERN_BOLLARD_VERSION, rv.output)
    assert re.search(PATTERN_DOCKER_CLIENT, rv.output)


PATTERN_BOLLARD_VERSION = r"""Bollard:
 Version: +\d+\.\d+\.\d+
"""

PATTERN_DOCKER_CLIENT = r"""Client:
 Cloud integration: +v\d+\.\d+\.\d+
 Version: +\d+\.\d+\.\d+
"""


def test_completion(runner):
    rv = runner.invoke(t.completion)
    assert rv.exit_code == 0
    assert "_bollard_completion" in rv.output
