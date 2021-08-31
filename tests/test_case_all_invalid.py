import os

import pytest
from pydantic import ValidationError

from tests.conftest import get_model

files = [file for file in os.scandir("./tests/cases/invalid")]


@pytest.mark.parametrize("file", files)
def test_raise_respo_exception(file: str):
    with pytest.raises(ValidationError):
        get_model(file)
    try:
        get_model(file)
    except ValidationError as exc:
        assert exc.errors()[0]["type"] == "value_error.respoexception"
