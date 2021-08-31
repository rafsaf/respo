import pytest
import yaml
from pathlib import Path
from respo.respo_model import RespoModel
from respo import logger


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    logger.warning(data)
    return RespoModel(**data)
