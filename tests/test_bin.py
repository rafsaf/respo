import os
from pathlib import Path

import pytest
from respo import get_respo_model
from respo.bin import _save_respo_model
from respo.config import config
from respo.helpers import RespoException

from tests.conftest import get_model


def test_model_is_equal_after_dumping():
    model1 = get_model("tests/cases/general.yml")
    _save_respo_model(model1)
    model2 = get_respo_model()
    assert model1 == model2


def test_exception_when_path_does_not_exist():
    with pytest.raises(RespoException):
        get_respo_model()
