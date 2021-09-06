import os
from os import DirEntry

import pytest
from respo.typer import app
from tests.conftest import get_model
from typer.testing import CliRunner

files = [file for file in os.scandir("./tests/cases/valid")]


@pytest.mark.parametrize("file", files)
def test_raise_respo_exception(file: DirEntry, runner: CliRunner):
    get_model(file.path)
    result = runner.invoke(app, [f"create", file.path])
    assert "Success!" in result.stdout