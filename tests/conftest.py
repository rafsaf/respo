import os
from pathlib import Path

import pytest
import yaml
from respo import RespoModel, get_respo_model
from respo.bin import _save_respo_model


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return RespoModel.parse_obj(data)


@pytest.fixture(scope="session")
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1, "test_respo.general.yml.bin")
    respo = get_respo_model("test_respo.general.yml.bin")
    yield respo
    os.remove("test_respo.general.yml.bin")
