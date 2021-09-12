from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from respo import RespoModel, config, get_respo_model, save_respo_model


@pytest.fixture(autouse=True)
def mock_env_variables_and_cleanup():
    config.RESPO_BINARY_FILE_NAME = "test_bin_respo.yml.bin"
    config.RESPO_DEFAULT_EXPORT_FILE = "test_export_respo"
    yield
    if Path(config.RESPO_BINARY_FILE_NAME).exists():
        Path(config.RESPO_BINARY_FILE_NAME).unlink()
    if Path(config.RESPO_DEFAULT_EXPORT_FILE + ".yml").exists():
        Path(config.RESPO_DEFAULT_EXPORT_FILE + ".yml").unlink()
    if Path(config.RESPO_DEFAULT_EXPORT_FILE + ".json").exists():
        Path(config.RESPO_DEFAULT_EXPORT_FILE + ".json").unlink()


def get_model(name: str) -> RespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return RespoModel.parse_obj(data)


@pytest.fixture
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    save_respo_model(model1)
    respo = get_respo_model()
    yield respo


@pytest.fixture()
def runner():
    runner = CliRunner()
    return runner
