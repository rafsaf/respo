import pathlib

import pytest
import yaml
from click import testing
import respo
from respo import cli


@pytest.fixture(autouse=True)
def mock_env_variables_and_cleanup(tmpdir):
    respo.config.RESPO_AUTO_FOLDER_NAME = f"{tmpdir}/auto"
    respo.config.RESPO_FILE_NAME_RESPO_MODEL = f"{tmpdir}/respo_model.py"


def get_model(name: str) -> respo.RespoModel:
    yml_file = pathlib.Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return respo.RespoModel.parse_obj(data)


@pytest.fixture
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    cli.save_respo_model(model1)
    return respo.RespoModel.get_respo_model()


@pytest.fixture()
def runner():
    return testing.CliRunner()
