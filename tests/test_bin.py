import os

from respo import get_respo_model
from respo.bin import _save_respo_model
from pathlib import Path
from tests.conftest import get_model
from respo.config import config


def test_model_is_equal_after_dumping():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1)
    model2 = get_respo_model()

    assert model1 == model2
    Path(config.RESPO_BINARY_FILE_NAME).unlink()
