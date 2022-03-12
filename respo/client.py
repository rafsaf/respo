from typing import Dict, List, Optional, Union

import ujson

from respo import core, exceptions, settings


class RespoClient:
    """Entity that can join a organization and be given a role.

    Implements methods for adding and removing roles and organization and special
    has_permission() for checking them using respo.RespoModel instance.

    Args:
        json_string: json serialized representation of dict with roles and
        organizations. At initialization deserialized using ujson.

    Examples:
        >>> RespoClient(None).dict()
        {"organizations": [], "roles": []}
        >>> RespoClient(
                '{"organizations":["test_org_x"],"roles":["test_org_x.test_role_y"]}'
            ).dict()
        {"organizations": ["test_org_x"], "roles": ["test_org_x.test_role_y"]}
        >>> str(RespoClient())
        '{"organizations":[],"roles":[]}'
        >>> RespoClient("I am invalid json")
        ValueError raised
    """

    def __init__(self, json_string: Optional[str] = "") -> None:
        self._value: Dict[str, List[str]] = {}
        self._json_string: str = json_string or ""
        if self._json_string == "":
            self._value = {"organizations": [], "roles": []}
        else:
            self._value = ujson.loads(self._json_string)

    def __str__(self) -> str:
        return ujson.dumps(self._value)

    def dict(self) -> Dict[str, List[str]]:
        """Returns dict representation of instance.

        Examples:
            >>> RespoClient().dict()
            {"organizations": [], "roles": []}
        """
        return self._value

    def roles(self) -> List[str]:
        """Lists instance `roles`.

        Examples:
            >>> respo_client.roles()
            []
            ["o1.some_role", "organization_default.admin", "default.root"]
        """
        return self._value["roles"]

    def organizations(self) -> List[str]:
        """Lists instance `organizations`.

        Examples:
            >>> respo_client.roles()
            []
            ["o1", "organization_default", "default"]
        """
        return self._value["organizations"]

    @staticmethod
    def validate_role(
        role_name: Union[str, core.Role], respo_model: core.RespoModel
    ) -> core.RoleLabel:
        """Validates role name for given RespoModel.

        Raises:
            ValueError: role_name is instance of str and doesn't match double
            label regex.
            RespoClientError: role_name does not exist in model.
        """
        role_label = core.RoleLabel(full_label=role_name)
        if role_label.full_label not in respo_model.ROLES:
            raise exceptions.RespoClientError(
                f"Role not found in respo model: {role_name}."
            )
        return role_label

    @staticmethod
    def validate_organization(
        organization_name: Union[str, core.Organization], respo_model: core.RespoModel
    ) -> core.OrganizationLabel:
        """Validates organization name for given RespoModel.

        Raises:
            ValueError: organization_name is instance of str and doesn't match single
            label regex.
            RespoClientError: organization_name does not exist in model.
        """
        organization_label = core.OrganizationLabel(full_label=organization_name)
        if organization_label.organization not in respo_model.ORGS:
            raise exceptions.RespoClientError(
                f"Organization not found in respo model: {organization_name}."
            )
        return organization_label

    def add_role(
        self,
        role_name: Union[str, core.Role],
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        """Adds role to this client after optional validation.

        Adds organization_name from the role_name if it doesn't exists.
        If validate_input is False, there will be no safe checks. It defaults to
        respo.config.RESPO_CHECK_FORCE and can be changed directly or using
        environment variable RESPO_CHECK_FORCE.

        Return:
            True: role was added.
            False: role already exists in the client.

        Raises:
            ValueError: role_name is instance of str and doesn't match double
            label regex.
            TypeError: respo_model is None when at the same time when
            validate_input is True.
            RespoClientError: role_name does not exist in the
            model (only with validation).

        Examples:
            >>> respo_client.add_role("default.sample_role")
            True
            >>> respo_client.add_role(
                    respo_model.ROLES.DEFAULT__SAMPLE_ROLE,
                    respo_model,
                    validate_input=False,
                )
            False
        """
        if validate_input and respo_model is not None:
            role_label = self.validate_role(
                role_name=role_name, respo_model=respo_model
            )
        elif validate_input and respo_model is None:
            raise TypeError("respo_model cannot be None when validate_input is True")
        else:
            role_label = core.RoleLabel(full_label=role_name)

        if role_label.organization not in self._value["organizations"]:
            self.add_organization(
                role_label.organization, respo_model=None, validate_input=False
            )
        if role_label.full_label in self._value["roles"]:
            return False
        else:
            self._value["roles"].append(role_label.full_label)
            return True

    def remove_role(
        self,
        role_name: Union[str, core.Role],
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        """Removes role from this client after optional validation.

        If validate_input is False, there will be no safe checks. It defaults to
        respo.config.RESPO_CHECK_FORCE and can be changed directly or using
        environment variable RESPO_CHECK_FORCE.

        Return:
            True: role was removed.
            False: role does not exists in the client.

        Raises:
            ValueError: role_name is instance of str and doesn't match double
            label regex.
            TypeError: respo_model is None when at the same time
            validate_input is True.
            RespoClientError: role_name does not exist in the
            model (only with validation).

        Examples:
            >>> respo_client.remove_role("default.sample_role")
            True
            >>> respo_client.remove_role(
                    respo_model.ROLES.DEFAULT__SAMPLE_ROLE,
                    respo_model,
                    validate_input=False,
                )
            False
        """
        if validate_input and respo_model is not None:
            role_label = self.validate_role(
                role_name=role_name, respo_model=respo_model
            )
        elif validate_input and respo_model is None:
            raise TypeError("respo_model cannot be None when validate_input is True")
        else:
            role_label = core.RoleLabel(full_label=role_name)

        if role_label.full_label in self._value["roles"]:
            self._value["roles"].remove(role_label.full_label)
            return True
        else:
            return False

    def add_organization(
        self,
        organization_name: Union[str, core.Organization],
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        """Adds organization to this client instance after optional validation.

        If validate_input is False, there will be no safe checks. It defaults to
        respo.config.RESPO_CHECK_FORCE and can be changed directly or using
        environment variable RESPO_CHECK_FORCE.

        Return:
            True: organization was added.
            False: organization already exists in client.

        Raises:
            ValueError: organization_name is instance of str and doesn't match single
            label regex.
            TypeError: respo_model is None when at the same time
            validate_input is True.
            RespoClientError: organization_name does not exist in
            the model (only with validation).

        Examples:
            >>> respo_client.add_organization("default")
            True
            >>> respo_client.add_organization(
                    respo_model.ORGS.DEFAULT, respo_model, validate_input=False
                )
            False
        """
        if validate_input and respo_model is not None:
            organization_label = self.validate_organization(
                organization_name=organization_name, respo_model=respo_model
            )
        elif validate_input and respo_model is None:
            raise TypeError("respo_model cannot be None when validate_input is True")
        else:
            organization_label = core.OrganizationLabel(full_label=organization_name)

        if organization_label.organization in self._value["organizations"]:
            return False
        else:
            self._value["organizations"].append(organization_label.organization)
            return True

    def remove_organization(
        self,
        organization_name: Union[str, core.Organization],
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        """Removes organization and all its roles after optional validation.

        Removes also all roles related to organization.
        If validate_input is False, there will be no safe checks. It defaults to
        respo.config.RESPO_CHECK_FORCE and can be changed directly or using
        environment variable RESPO_CHECK_FORCE.

        Return:
            True: organization was removed.
            False: organization does not exists in the client.

        Raises:
            ValueError: organization_name is instance of str and doesn't match single
            label regex.
            TypeError: respo_model is None when at the same time
            validate_input is True.
            RespoClientError: organization_name does not exist
            the in model (only with validation).

        Examples:
            >>> respo_client.remove_organization("default")
            True
            >>> respo_client.remove_organization(
                    respo_model.ORGS.DEFAULT, respo_model, validate_input=False
                )
            False
        """
        if validate_input and respo_model is not None:
            organization_label = self.validate_organization(
                organization_name=organization_name, respo_model=respo_model
            )
        elif validate_input and respo_model is None:
            raise TypeError("respo_model cannot be None when validate_input is True")
        else:
            organization_label = core.OrganizationLabel(full_label=organization_name)

        if organization_label.organization in self._value["organizations"]:
            self._value["organizations"].remove(organization_label.organization)

            new_roles: List[str] = []
            for role in self._value["roles"]:
                if not role.startswith(f"{organization_name}."):
                    new_roles.append(role)
            self._value["roles"] = new_roles
            return True
        else:
            return False

    def has_permission(
        self, permission_name: str, respo_model: core.RespoModel
    ) -> bool:
        """Checks if *this* client does have specific permission.

        Under the hood searches through prepared as pickled file dicts to
        speed this up (after resolving the complex nested rules logic etc).
        For very large self._value this can be pretty slow anyway.

        Return:
            True: client has permission.
            False: client doesn't have permission.

        Raises:
            ValueError: permission_name doesn't match triple label regex.

        Examples:
            >>> respo_client.has_permission("default.users.read", respo_model)
            True
            >>> respo_client.has_permission(
                    respo_model.PERMS.DEFAULT__USERS__READ_ALL, respo_model
                )
            True
        """
        permission_label = core.PermissionLabel(permission_name)

        role_to_check = permission_label.to_role()
        if not permission_label.organization in self._value["organizations"]:
            return False
        if role_to_check not in self._value["roles"]:
            return False
        if not role_to_check in respo_model.roles_labels:
            self.remove_role(role_to_check, validate_input=False)
            return False
        if permission_label.label in respo_model.roles_labels[role_to_check]:
            return True
        return False
