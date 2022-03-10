from typing import Dict, List, Optional, Union

import ujson

from respo.config import config
from respo.helpers import RespoException, RoleLabel
from respo.respo_model import BaseRespoModel, Organization, Role


class RespoClient:
    """
    Main class that represent single client, user, unit or any entity
    that can join a organization or be given a role allowing access to resources.
    """

    def __init__(self, json_string: Optional[str] = "") -> None:
        """
        Main class that represent single client, user, unit or any entity
        that can join a organization or be given a role allowing access to resources.

        Implements adding and removing roles and organizations methods and `has_permission`
        to validate access. Note, neither `_json_string` nor `_value` should be ever changed directly.
        If `json_string` is None or empty string, `_value` will be equal to `{"organizations": [], "roles": []}`.

        Args:
            json_string (Optional[str]): `str` serialized representation of dict
            with roles and organizations. It then always get deserialized using `ujson.loads`
            to dictionary.

        Examples of json_string :
        ```
        json_string = None
        json_string = ""
        json_string = '{"organizations":["test_org_x"],"roles":["test_org_x.test_role_y"]}'
        json_string = "Not a json" # INVALID, ValueError will be raised
        ```

        """
        self._value: Dict[str, List[str]] = {}
        self._json_string: str = json_string or ""
        if self._json_string == "":
            self._value = {"organizations": [], "roles": []}
        else:
            self._value = ujson.loads(self._json_string)

    def dict(self):
        """
        Dict representation of instance.

        Example return:
        ```
        {"organizations": ["o1", "o2"], "roles": ["o1.role1"]}
        ```
        """
        return self._value

    def roles(self):
        """
        List representing this instance `roles`.

        Example return:
        ```
        ["o1.some_role", "organization_default.admin", "default.root"]
        ```
        Note, the first part of each string IS ALWAYS one of the client's organizations,
        in this case calling `self.organizations()` will return:
        ```
        [..., "o1", ..., "organization_default", ..., "default", ...]
        ```
        """
        return self._value["roles"]

    def organizations(self):
        """
        List representing this instance `organizations`.

        Example return:
        ```
        ["o1", "organization_default", "default"]
        ```
        """
        return self._value["organizations"]

    @staticmethod
    def validate_role(role_label: RoleLabel, respo_model: Optional[BaseRespoModel]):
        """Validates `role`

        Raises:
            `respo.RespoException`: when `respo_model` is None
            `respo.RespoException`: when role does not exists for provided model

        Examples:
        ```
        from respo import RoleLabel, BaseRespoModel, RespoClient

        model = BaseRespoModel.get_respo_model()
        label = RoleLabel("organization_name.role_name")

        RespoClient.validate_role(label, model)
        ```
        """
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
        organization_name: str, respo_model: Optional[BaseRespoModel]
    ):
        """Validates `organization`

        Raises:
            `respo.RespoException`: when `respo_model` is None
            `respo.RespoException`: when organization does not exists for provided model

        Examples:
        ```
        from respo import BaseRespoModel, RespoClient

        model = BaseRespoModel.get_respo_model()

        RespoClient.validate_organization("my_organization", model)
        ```
        """
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
        role_name: Union[str, Role],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        """
        Adds `role_name` to this client instance. `respo_model` can be both `str` and `respo.Role` instance.
        See examples below. `respo_model` is required when `validate_input` is True, then input role_name
        will be additinaly validated. `validate_input` defaults to `respo.config.RESPO_CHECK_FORCE`.

        When `validate_input` is False, there will be no safe checks!

        Return:
            `True`: when role was added and it didn't exist.
            `False`: when role is already bound to the client

        Raises:
            `pydantic.ValidationError`: when role_name is invalid
            `respo.RespoException`: when `respo_model` is `None` and validate_input is `True`
            `respo.RespoException`: when validate_input is `True` and role doen not exist for provided model
            `respo.RespoException`: when organization wasn't earlier added using `self.add_organization`

        Examples:
        ```
        from respo_model import RespoModel

        respo_model = RespoModel.get_respo_model()
        respo_client = RespoClient()

        assert respo_client.add_role("org.role1", validate_input=False)
        assert not respo_client.add_role("org.role1", validate_input=False) # False because it was already added
        assert respo_client.add_role("org.role", respo_model, validate_input=True)
        assert respo_client.add_role(respo_model.ROLES.DEFAULT__SOME_ROLE, respo_model, validate_input=True)
        ```
        """
        role_name = str(role_name)
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
        role_name: Union[str, Role],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        """
        Removes `role_name` from this client instance. `respo_model` can be both `str` and `respo.Role` instance.
        See examples below. `respo_model` is required when `validate_input` is True, then input role_name
        will be additinaly validated. `validate_input` defaults to `respo.config.RESPO_CHECK_FORCE`.

        When `validate_input` is False, there will be no safe checks!

        Return:
            `True`: when role removed.
            `False`: when role does not exist in this client instance

        Raises:
            `pydantic.ValidationError`: when role_name is invalid
            `respo.RespoException`: when `respo_model` is `None` and validate_input is `True`
            `respo.RespoException`: when validate_input is `True` and role does not exist for provided model

        Examples:
        ```
        from respo_model import RespoModel

        respo_model = RespoModel.get_respo_model()
        respo_client = RespoClient()

        assert respo_client.remove_role("org.role1", validate_input=False)
        assert not respo_client.remove_role("org.role1", validate_input=False) # False because it was already removed
        assert respo_client.remove_role("org.role", respo_model, validate_input=True)
        assert respo_client.remove_role(respo_model.ROLES.DEFAULT__SOME_ROLE, respo_model, validate_input=True)
        ```
        """
        role_name = str(role_name)
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
        organization_name: Union[str, Organization],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        organization_name = str(organization_name)
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
        organization_name: Union[str, Organization],
        respo_model: Optional[BaseRespoModel] = None,
        validate_input: bool = config.RESPO_CHECK_FORCE,
    ) -> bool:
        organization_name = str(organization_name)
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
        self, full_permission_name: str, respo_model: BaseRespoModel
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
