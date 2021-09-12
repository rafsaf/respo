import os
from os import DirEntry

import pytest
from respo import app
from typer.testing import CliRunner

from tests.conftest import get_model

files = [file for file in os.scandir("./tests/cases/valid")]


@pytest.mark.parametrize("file", files)
def test_raise_respo_exception(file: DirEntry, runner: CliRunner):
    get_model(file.path)
    result = runner.invoke(app, ["create", file.path])
    assert "Success!" in result.stdout
