from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from respo import BaseRespoModel, config, save_respo_model


@pytest.fixture(autouse=True)
def mock_env_variables_and_cleanup(tmpdir):
    config.RESPO_AUTO_FOLDER_NAME = f"{tmpdir}/auto"
    config.RESPO_FILE_NAME_RESPO_MODEL = f"{tmpdir}/respo_model.py"


def get_model(name: str) -> BaseRespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return BaseRespoModel.parse_obj(data)


@pytest.fixture
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    save_respo_model(model1)
    respo = BaseRespoModel.get_respo_model()
    yield respo


@pytest.fixture()
def runner():
    return CliRunner()
