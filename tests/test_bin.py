from respo import get_respo_model
from respo.bin import _save_respo_model
from tests.utils import get_model
import os


def test_model_is_equal_after_dumping():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1, "test_respo.bin")
    model2 = get_respo_model("test_respo.bin")

    assert model1 == model2
    os.remove("test_respo.bin")
