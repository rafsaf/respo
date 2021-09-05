import os
from os import DirEntry

import pytest
from pydantic import ValidationError
from respo.typer import app
from tests.conftest import get_model
from typer.testing import CliRunner

files = [file for file in os.scandir("./tests/cases/invalid")]


@pytest.mark.parametrize("file", files)
def test_raise_respo_exception(file: DirEntry, runner: CliRunner):
    with pytest.raises(ValidationError):
        get_model(file.path)
    try:
        get_model(file.path)
    except ValidationError as exc:
        assert exc.errors()[0]["type"] == "value_error.respoexception"

    result = runner.invoke(app, [f"create", file.path])
    assert "Could not validate data" in result.stdout