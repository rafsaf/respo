from pydantic import BaseSettings


class Config(BaseSettings):
    RESPO_BINARY_FILE_NAME: str = "__auto__respo_model.bin"


config = Config()
