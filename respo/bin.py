import pickle
from pathlib import Path
from respo.respo_model import RespoModel
from respo.helpers import RespoException

BINARY_FILE_NAME = "__auto__respo_model.bin"
binary_file_path = Path(BINARY_FILE_NAME)


def get_respo_model(_Path: str = BINARY_FILE_NAME) -> RespoModel:
    if not binary_file_path.exists():
        raise RespoException(
            f"{BINARY_FILE_NAME} file does not exist. Did you forget to create it?"
        )
    with open(_Path, "rb") as file:
        model = pickle.load(file)
    return model


def _save_respo_model(model: RespoModel, _Path: str = BINARY_FILE_NAME) -> None:
    with open(_Path, "wb") as file:
        pickle.dump(model, file)
