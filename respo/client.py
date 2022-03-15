from typing import List, Optional

from respo import core, exceptions, settings


class RespoClient:
    """Entity that can be given a role.

    Implements methods for adding and removing roles and method
    has_permission() for checking them using respo.RespoModel instance.

    Args:
        roles_str: string with roles separated by comma

    Examples:
        >>> RespoClient(None).roles
        []
        >>> RespoClient("abc,def").roles
        ["abc", "def"]
        >>> str(RespoClient("abc,def"))
        "abc,def"
    """

    def __init__(self, roles_str: Optional[str] = "") -> None:
        if not roles_str:
            self.roles: List[str] = []
        else:
            self.roles: List[str] = roles_str.split(",")

    def __str__(self) -> str:
        return ",".join(self.roles)

    @staticmethod
    def validate_role(role_name: str, respo_model: core.RespoModel) -> core.RoleLabel:
        """Validates role name.

        Raises:
            ValueError: role_name is instance of str and doesn't match single
            label regex.
            RespoClientError: role_name does not exist in model.
        """
        role_label = core.RoleLabel(role_name=role_name)
        if role_label.role_label not in respo_model.ROLES:
            raise exceptions.RespoClientError(
                f"Role not found in respo model: {role_name}."
            )
        return role_label

    def add_role(
        self,
        role_name: str,
        respo_model: Optional[core.RespoModel] = None,
        validate_input: bool = settings.config.RESPO_CHECK_FORCE,
    ) -> bool:
        """Adds role to this client after optional validation.

        If validate_input is False, there will be no safe checks. It defaults to
        respo.config.RESPO_CHECK_FORCE and can be changed directly or using
        environment variable RESPO_CHECK_FORCE.

        Return:
            True: role was added.
            False: role already exists in the client.

        Raises:
            ValueError: role_name is instance of str and doesn't single
            label regex.
            TypeError: respo_model is None when at the same time when
            validate_input is True.
            RespoClientError: role_name does not exist in the
            model (only with validation).

        Examples:
            >>> respo_client.add_role("sample_role", validate_input=False)
            True
            >>> respo_client.add_role(
                    respo_model.ROLES.SAMPLE_ROLE,
                    respo_model,
                    validate_input=True,
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
            role_label = core.RoleLabel(role_name=role_name)

        if role_label.role_label in self.roles:
            return False
        else:
            self.roles.append(role_label.role_label)
            return True

    def remove_role(
        self,
        role_name: str,
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
            ValueError: role_name is instance of str and doesn't single
            label regex.
            TypeError: respo_model is None when at the same time
            validate_input is True.
            RespoClientError: role_name does not exist in the
            model (only with validation).

        Examples:
            >>> respo_client.remove_role("sample_role", validate_input=False)
            True
            >>> respo_client.remove_role(
                    respo_model.ROLES.SAMPLE_ROLE,
                    respo_model,
                    validate_input=True,
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
            role_label = core.RoleLabel(role_name=role_name)

        if role_label.role_label in self.roles:
            self.roles.remove(role_label.role_label)
            return True
        else:
            return False

    def has_permission(
        self, permission_name: str, respo_model: core.RespoModel
    ) -> bool:
        """Checks if *this* client does have specific permission.

        Under the hood searches through prepared role-permissions dict to
        speed this up (after resolving the complex nested rules logic etc).
        For very large self.roles this can be pretty slow anyway.

        Return:
            True: client has permission.
            False: client doesn't have permission.

        Raises:
            ValueError: permission_name doesn't match double label regex.

        Examples:
            >>> respo_client.has_permission("users.read", respo_model)
            True
            >>> respo_client.has_permission(
                    respo_model.PERMS.USERS__READ_ALL, respo_model
                )
            True
        """
        permission_label = core.PermissionLabel(permission_name)
        for role in self.roles:
            if permission_label.permission_name in respo_model.ROLES.permissions(role):
                return True
        return False
