import os
from respo import get_respo_model, create_respo_client
from respo.bin import _save_respo_model
from tests.utils import get_model


def test_general_yml():
    model1 = get_model("tests/cases/general.yml")

    _save_respo_model(model1, "test_respo1.bin")
    respo = get_respo_model("test_respo1.bin")

    client = create_respo_client(organization="book123", role="client")
    assert respo.check("book123.user.all", client) is False

    os.remove("test_respo.bin")
