import os
from os import DirEntry

import pytest
from click.testing import CliRunner

from respo.cli import app
from tests.conftest import get_model

files = [file for file in os.scandir("./tests/cases/valid")]


@pytest.mark.parametrize("file", files)
def test_all_models_valid(file: DirEntry, runner: CliRunner):
    get_model(file.path)
    result = runner.invoke(app, ["create", file.path])
    assert "Success!" in result.stdout
