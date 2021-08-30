import pytest
import yaml
from pathlib import Path
from respo.respo_model import RespoModel


@pytest.fixture
def get_model():
    def _get_model(name: str) -> RespoModel:
        yml_file = Path(name)
        data = yaml.safe_load(yml_file.read_text())
        return RespoModel(**data)

    return _get_model
