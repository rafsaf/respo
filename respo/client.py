import logging
from typing import Dict, List, Optional

import ujson

from respo.helpers import RespoException, RoleLabel
from respo.respo_model import RespoModel
import itertools


class RespoClient:
    count_id = itertools.count()

    def __init__(self, json_string: Optional[str] = "") -> None:
        self._value: Dict[str, List[str]] = {}
        self._initialized: bool = False
        self._json_string: str = json_string or ""
        if self._json_string == "":
            self._value = {"organizations": [], "roles": []}
            self._initialized = True

    def __str__(self) -> str:
        return ujson.dumps(self._value)

    def _load(self):
        if not self._initialized:
            self._value = ujson.loads(self._json_string)
            self._initialized = True

    def roles(self):
        self._load()
        return self._value["roles"]

    def organizations(self):
        self._load()
        return self._value["organizations"]

    def add_role(
        self,
        role_name: str,
        respo_model: RespoModel,
        validate_input: bool = True,
    ):
        self._load()
        role_label = RoleLabel(full_label=role_name)
        if validate_input:
            if not respo_model.role_exists(
                role_name=role_label.role, organization_name=role_label.organization
            ):
                raise RespoException(
                    f"Could not add role {role_name}."
                    f" Role not found in organization {role_label.organization}"
                )
        if role_label.organization not in self._value["organizations"]:
            raise RespoException(
                f"Could not add role {role_name}."
                f" Organization {role_label.organization} must be added to this RespoClient before adding role."
            )
        if role_name in self._value["roles"]:
            raise RespoException(f"Already have the role {role_name}.")
        self._value["roles"].append(role_name)
        self.id = next(self.count_id)

    def add_organization(
        self,
        organization_name: str,
        respo_model: RespoModel,
        validate_input: bool = True,
    ):
        self._load()
        if validate_input:
            if not respo_model.organization_exists(organization_name):
                raise RespoException(
                    f"Could not add organization {organization_name}."
                    f" Organization {organization_name} not found in respo model"
                )
        if organization_name in self._value["organizations"]:
            raise RespoException(f"Already have organization {organization_name}.")
        self._value["organizations"].append(organization_name)
        self.id = next(self.count_id)

    def has_permission(self, full_permission_name: str, respo_model: RespoModel):
        self._load()
        for role in self._value["roles"]:
            if role in respo_model.permission_to_role_dict[full_permission_name]:
                return True
        for organization in self._value["organizations"]:
            if (
                organization
                in respo_model.permission_to_organization_dict[full_permission_name]
            ):
                return True
        return False
