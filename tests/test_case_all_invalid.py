import os
from os import DirEntry

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from respo.cli import app
from tests.conftest import get_model

files = [file for file in os.scandir("./tests/cases/invalid")]


@pytest.mark.parametrize("file", files)
def test_raise_respo_exception(file: DirEntry, runner: CliRunner):
    with pytest.raises(ValidationError):
        get_model(file.path)
    try:
        get_model(file.path)
    except ValidationError as exc:
        assert exc.errors()[0]["type"] in [
            "value_error.respo",
            "value_error.str.regex",
            "value_error.const",
        ]

    result = runner.invoke(app, ["create", file.path])
    assert "Could not validate respo model" in result.stdout
