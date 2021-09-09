from pydantic import BaseSettings


class Config(BaseSettings):
    RESPO_BINARY_FILE_NAME: str = ".respo_cache/__auto__respo_model.bin"
    RESPO_DEFAULT_EXPORT_FILE: str = "__auto__respo_model"
    RESPO_CHECK_FORCE: bool = False


config = Config()
