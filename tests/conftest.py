import os
from pathlib import Path

import pytest
import yaml
from respo import RespoModel, get_respo_model
from respo.bin import _save_respo_model
from respo.config import config


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return RespoModel.parse_obj(data)


os.environ["RESPO_BINARY_FILE_NAME"] = "test_respo.general.yml.bin"


@pytest.fixture
def get_general_model():

    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1)
    respo = get_respo_model()
    yield respo
    Path(config.RESPO_BINARY_FILE_NAME).unlink()
