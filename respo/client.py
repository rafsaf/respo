from typing import Dict, List, Optional

import ujson

from respo.helpers import RespoException, RoleLabel
from respo.respo_model import RespoModel
from respo.config import config


class RespoClient:
    def __init__(self, json_string: Optional[str] = "") -> None:
        self._value: Dict[str, List[str]] = {}
        self._json_string: str = json_string or ""
        if self._json_string == "":
            self._value = {"organizations": [], "roles": []}
            self._initialized = True
        else:
            self._value = ujson.loads(self._json_string)

    def dict(self):
        return self._value

    def roles(self):
        return self._value["roles"]

    def organizations(self):
        return self._value["organizations"]

    @staticmethod
    def validate_role(role_label: RoleLabel, respo_model: Optional[RespoModel]):
        if respo_model is None:
            raise RespoException(
                f"Error in validate_role: {role_label.full_label}."
                " Parameter `respo_model` cannot be None"
            )
        if not respo_model.role_exists(
            role_name=role_label.role, organization_name=role_label.organization
        ):
            raise RespoException(
                f"Error in validation: {role_label.full_label}."
                f" Role not found in organization {role_label.organization}"
            )

    @staticmethod
    def validate_organization(
        organization_name: str, respo_model: Optional[RespoModel]
    ):
        if respo_model is None:
            raise RespoException(
                f"Error in validate_organization: {organization_name}."
                " Parameter `respo_model` cannot be None"
            )
        if not respo_model.organization_exists(organization_name):
            raise RespoException(
                f"Could not add organization {organization_name}."
                f" Organization {organization_name} not found in respo model"
            )

    def add_role(
        self,
        role_name: str,
        respo_model: Optional[RespoModel],
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        role_label = RoleLabel(full_label=role_name)
        if validate_input:
            self.validate_role(role_label=role_label, respo_model=respo_model)

        if role_label.organization not in self._value["organizations"]:
            raise RespoException(
                f"Could not add role {role_name}."
                f" Organization {role_label.organization} must"
                " be added to this RespoClient before adding role."
            )
        if role_name in self._value["roles"]:
            return False
        else:
            self._value["roles"].append(role_name)
            return True

    def remove_role(
        self,
        role_name: str,
        respo_model: Optional[RespoModel],
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        role_label = RoleLabel(full_label=role_name)
        if validate_input:
            self.validate_role(role_label=role_label, respo_model=respo_model)

        if role_name in self._value["roles"]:
            self._value["roles"].remove(role_name)
            return True
        else:
            return False

    def add_organization(
        self,
        organization_name: str,
        respo_model: Optional[RespoModel],
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        if validate_input:
            self.validate_organization(
                organization_name=organization_name, respo_model=respo_model
            )
        if organization_name in self._value["organizations"]:
            return False
        else:
            self._value["organizations"].append(organization_name)
            return True

    def remove_organization(
        self,
        organization_name: str,
        respo_model: Optional[RespoModel],
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        if validate_input:
            self.validate_organization(
                organization_name=organization_name, respo_model=respo_model
            )
        if organization_name in self._value["organizations"]:
            self._value["organizations"].remove(organization_name)
            return True
        else:
            return False

    def has_permission(
        self, full_permission_name: str, respo_model: RespoModel
    ) -> bool:
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

    def __str__(self) -> str:
        return ujson.dumps(self._value)
