from pathlib import Path

import toml

from respo import __version__


def test_version_match_pyproject_toml():
    PROJECT_DIR = Path(__file__).parent.parent
    PYPROJECT_CONTENT = toml.load(f"{PROJECT_DIR}/pyproject.toml")["tool"]["poetry"]
    assert PYPROJECT_CONTENT["version"] == __version__
