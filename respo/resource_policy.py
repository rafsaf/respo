from pydantic import BaseModel
from respo.resource_model import ResourceModel, Client
from respo.helpers import ResourcePolicyException, logger
from typing import Dict, List, Optional, Union
import yaml
import json
import os
import atexit


def _save_to_file_on_exit(path: str, resource_policy: ResourceModel):
    if not os.path.exists(path):
        logger.warning(f"{path} does not exist, it will be created")
    with open(path, "w") as stream:
        try:
            file = yaml.dump(resource_policy.dict())
            stream.write(file)
        except Exception as e:
            raise ResourcePolicyException(str(e) + f"\nCould not write to file {path}")


def get_respo_model(
    path_to_yml: Optional[str] = None,
    path_to_json: Optional[str] = None,
    python_dict: Optional[Dict] = None,
    read_only: bool = False,
    _PATH: str = "__auto__resource_policy.yml",
):
    if read_only or os.path.exists(_PATH):
        path_to_yml = _PATH
    if path_to_yml:
        with open(path_to_yml, "r") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:

                raise ResourcePolicyException(
                    str(exc) + f"\nCan't load yml file {path_to_yml}"
                )
    elif path_to_json:
        with open(path_to_json, "r") as json_file:
            try:
                data = json.loads(json_file.read())
            except Exception as exc:
                raise ResourcePolicyException(
                    str(exc) + f"Can't load json file {path_to_json}"
                )
    elif python_dict:
        data = python_dict
    else:
        raise ResourcePolicyException("Please provide any of supported methods")

    resource_policy = ResourceModel(**data)
    if not read_only:
        atexit.register(
            _save_to_file_on_exit,
            path=_PATH,
            resource_policy=resource_policy,
        )
        if os.path.exists(_PATH):
            logger.warning(f"read_only is set to False. {_PATH} has been overwritten")
    return resource_policy


def create_respo_client(
    pk: Optional[Union[List[str], str]] = None,
    organization: Optional[Union[List[str], str]] = None,
    role: Optional[Union[List[str], str]] = None,
):
    return Client(pk=pk, organization=organization, role=role)
