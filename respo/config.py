from pydantic import BaseSettings


class Config(BaseSettings):
    RESPO_AUTO_FOLDER_NAME: str = ".respo_cache"
    RESPO_AUTO_BINARY_FILE_NAME: str = "__auto__respo_model.bin"
    RESPO_AUTO_YML_FILE_NAME: str = "__auto__respo_model.yml"

    RESPO_DEFAULT_EXPORT_FILE: str = "generated_respo_model"
    RESPO_CHECK_FORCE: bool = False
    RESPO_FILE_NAME_RESPO_MODEL: str = "respo_model.py"


config = Config()
