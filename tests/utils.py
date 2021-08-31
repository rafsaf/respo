from pathlib import Path

import yaml
from respo.respo_model import RespoModel


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return RespoModel.parse_obj(data)
