import pickle
from pathlib import Path

from respo.helpers import RespoException
from respo.respo_model import RespoModel
from respo.config import config


def get_respo_model() -> RespoModel:
    if not Path(config.RESPO_BINARY_FILE_NAME).exists():
        raise RespoException(
            f"{config.RESPO_BINARY_FILE_NAME} file does not exist. Did you forget to create it?"
        )
    with open(config.RESPO_BINARY_FILE_NAME, "rb") as respo_model_file:
        model = pickle.load(respo_model_file)
    return model


def _save_respo_model(model: RespoModel) -> None:
    with open(config.RESPO_BINARY_FILE_NAME, "wb") as file:
        pickle.dump(model, file)
