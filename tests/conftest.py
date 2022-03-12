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


@pytest.fixture(params=[True, False])
def get_general_model(request):
    model1 = get_model("tests/cases/general.yml")

    cli.save_respo_model(model1)
    res = respo.RespoModel.get_respo_model(yml_file=request.param)
    from sys import getsizeof

    print(getsizeof(res))
    return res


@pytest.fixture()
def runner():
    return testing.CliRunner()
