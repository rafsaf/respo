import os

import pytest
from respo.bin import _save_respo_model, get_respo_model

from tests.utils import get_model


@pytest.fixture(scope="session")
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1, "test_respo.general.yml.bin")
    respo = get_respo_model("test_respo.general.yml.bin")
    yield respo
    os.remove("test_respo.general.yml.bin")
