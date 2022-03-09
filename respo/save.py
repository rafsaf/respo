import pickle
from pathlib import Path

import yaml

from respo.config import config
from respo.respo_model import BaseRespoModel


def save_respo_model(model: BaseRespoModel) -> None:
    path_bin = Path(
        f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}"
    )
    path_yml = Path(
        f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_YML_FILE_NAME}"
    )
    Path(config.RESPO_AUTO_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

    with open(path_bin, "wb") as file:
        pickle.dump(model, file)

    with open(path_yml, "w") as file:
        yaml.dump(
            model.dict(
                exclude={
                    "permission_to_organization_dict",
                    "permission_to_role_dict",
                    "PERMS",
                    "ORGS",
                    "ROLES",
                }
            ),
            file,
        )
