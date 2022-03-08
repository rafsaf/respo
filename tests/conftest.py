from os import unlink
from pathlib import Path
from shutil import rmtree

import pytest
import yaml
from typer.testing import CliRunner

from respo import BaseRespoModel, config, save_respo_model


@pytest.fixture(autouse=True)
def mock_env_variables_and_cleanup():
    config.RESPO_AUTO_BINARY_FILE_NAME = "test_bin_respo.bin"
    config.RESPO_AUTO_FOLDER_NAME = ".respo_test_cache"
    config.RESPO_AUTO_YML_FILE_NAME = "test_yml_respo.yml"
    config.RESPO_DEFAULT_EXPORT_FILE = "test_export_respo"
    config.RESPO_CHECK_FORCE = True

    def cleanup():
        rmtree(config.RESPO_AUTO_FOLDER_NAME, ignore_errors=True)
        try:
            unlink(f"{config.RESPO_DEFAULT_EXPORT_FILE}.json")
        except FileNotFoundError:
            pass
        try:
            unlink(f"{config.RESPO_DEFAULT_EXPORT_FILE}.yml")
        except FileNotFoundError:
            pass

    cleanup()
    yield
    cleanup()


def get_model(name: str) -> BaseRespoModel:
    yml_file = Path(name)
    data = yaml.safe_load(yml_file.read_text())
    return BaseRespoModel.parse_obj(data)


@pytest.fixture
def get_general_model():
    model1 = get_model("tests/cases/general.yml")

    save_respo_model(model1)
    respo = BaseRespoModel.get_respo_model()
    yield respo


@pytest.fixture()
def runner():
    return CliRunner()
