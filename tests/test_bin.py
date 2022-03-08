from respo import BaseRespoModel, save_respo_model
from tests.conftest import get_model


def test_model_is_equal_after_dumping():
    model1 = get_model("tests/cases/general.yml")
    save_respo_model(model1)
    model2 = BaseRespoModel.get_respo_model()
    assert model1 == model2
