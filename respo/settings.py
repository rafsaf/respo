import pathlib

import pydantic


class Config(pydantic.BaseSettings):
    """Config for respo based on evironment variables.

    Args:
        RESPO_AUTO_FOLDER_NAME: folder with pickled respo model
        RESPO_AUTO_BINARY_FILE_NAME: file name of pickled model in auto folder
        RESPO_CHECK_FORCE: require strict validation in respo.RespoClient methods
        RESPO_FILE_NAME_RESPO_MODEL: name of exported python file
    """

    RESPO_AUTO_FOLDER_NAME: str = ".respo_cache"
    RESPO_AUTO_BINARY_FILE_NAME: str = "__auto__respo_model.bin"

    RESPO_CHECK_FORCE: bool = True
    RESPO_FILE_NAME_RESPO_MODEL: str = "respo_model.py"

    @property
    def path_bin_file(self):
        return pathlib.Path(
            f"{self.RESPO_AUTO_FOLDER_NAME}/{self.RESPO_AUTO_BINARY_FILE_NAME}"
        )

    @property
    def path_python_file(self):
        return pathlib.Path(self.RESPO_FILE_NAME_RESPO_MODEL)


config = Config()
