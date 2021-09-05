from pathlib import Path

import pytest
import yaml
from respo import RespoModel, get_respo_model
from respo.bin import _save_respo_model
from respo.config import config


@pytest.fixture(autouse=True)
def mock_env_variables_and_cleanup():
    config.RESPO_BINARY_FILE_NAME = "test_bin_respo.yml.bin"
    config.RESPO_DEFAULT_EXPORT_FILE = "test_export_respo.yml"
    yield
    if Path(config.RESPO_BINARY_FILE_NAME).exists():
        Path(config.RESPO_BINARY_FILE_NAME).unlink()


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return RespoModel.parse_obj(data)


@pytest.fixture
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1)
    respo = get_respo_model()
    yield respo
