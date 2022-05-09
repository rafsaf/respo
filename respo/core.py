import pickle
import re
from typing import Dict, Iterator, List, Optional, Set

import pydantic
import yaml

from respo import exceptions, settings

SINGLE_LABEL_REGEX = re.compile(r"^[a-z_0-9]{1,}$")
DOUBLE_LABEL_REGEX = re.compile(r"^[a-z_0-9]{1,}\.[a-z_0-9]{1,}$")


class SingleLabel(pydantic.ConstrainedStr):
    regex = SINGLE_LABEL_REGEX
    max_length = 128


class DoubleDotLabel(pydantic.ConstrainedStr):
    regex = DOUBLE_LABEL_REGEX
    max_length = 128


class PermissionLabel:
    """Helper class for double (permission) labels validation.

    Examples:
        >>> PermissionLabel("x.y")
        OK
        >>> PermissionLabel("x")
        ValueError
        >>> PermissionLabel("%^asd")
        ValueError
        >>> PermissionLabel("collection_part.label_part").collection
        "collection_part"
    """

    def __init__(self, permission_name: str) -> None:
        if DOUBLE_LABEL_REGEX.fullmatch(permission_name) is None:
            raise ValueError(
                f"Permission does not match {DOUBLE_LABEL_REGEX} regex: {permission_name}"
            )
        permission_name_split = permission_name.split(".")
        self.collection = permission_name_split[0]
        self.label = permission_name_split[1]
        self.permission_name = permission_name

    def __str__(self):
        return self.permission_name


class RoleLabel:
    """Helper class for single (role) labels validation.

    Examples:
        >>> RoleLabel("role_text")
        OK
        >>> RoleLabel("double.bad")
        ValueError
        >>> RoleLabel("valid").role_label
        "valid"
    """

    def __init__(self, role_name: str) -> None:
        if SINGLE_LABEL_REGEX.fullmatch(role_name) is None:
            raise ValueError(
                f"Role does not match {SINGLE_LABEL_REGEX} regex: {role_name}"
            )
        self.role_label = role_name

    def __str__(self):
        return self.role_label


class LabelsContainer:
    """Container for respo model attributes with respo_model in init

    Stores human friendly dict with attrs in __dict__ that can be
    accessed via attributes.

    Examples:
        >>> attrs_container = LabelsContainer()
        >>> attrs_container._add_item("valid_text")
        >>> attrs_container.VALID_TEXT
        "valid_text"
    """

    def __init__(self, respo_model: "RespoModel") -> None:
        self.respo_model: RespoModel = respo_model

    def _add_item(self, label: str) -> None:
        self.__dict__[label.upper().replace(".", "__")] = label


class PERMSContainer(LabelsContainer):
    """LabelsContainer variation for PERMS"""

    def __iter__(self) -> Iterator[str]:
        return iter(self.respo_model.permissions)

    def __str__(self) -> str:
        return str(self.respo_model.permissions)

    def __contains__(self, key: str) -> bool:
        return key in self.respo_model.permissions

    def __len__(self):
        return len(self.respo_model.permissions)

    def __eq__(self, other: object):
        if not isinstance(other, PERMSContainer):
            raise ValueError(f"Cannot comapre to other instance: {other}")
        return self.respo_model.permissions == other.respo_model.permissions


class ROLESContainer(LabelsContainer):
    """LabelsContainer variation for ROLES"""

    def __iter__(self) -> Iterator[str]:
        return iter(self.respo_model.roles_permissions)

    def __str__(self) -> str:
        return str(self.respo_model.roles_permissions)

    def __contains__(self, key: str) -> bool:
        return key in self.respo_model.roles_permissions

    def permissions(self, role_name: str) -> List[str]:
        if role_name in self:
            return self.respo_model.roles_permissions[role_name]
        raise exceptions.RespoModelError(
            "Could not get permissions for role\n"
            f"Role does not exist in respo model: {role_name}"
        )

    def __eq__(self, other: object):
        if not isinstance(other, ROLESContainer):
            raise ValueError(f"Cannot comapre to other instance: {other}")
        return self.respo_model.roles_permissions == other.respo_model.roles_permissions

    def __len__(self):
        return len(self.respo_model.roles_permissions)


class Role(pydantic.BaseModel):
    """Represents single role in yml file."""

    name: SingleLabel
    include: Optional[List[SingleLabel]] = None
    permissions: List[DoubleDotLabel]


class Principle(pydantic.BaseModel):
    """Represents single principle in yml file."""

    when: DoubleDotLabel
    then: List[DoubleDotLabel]


class RespoModel(pydantic.BaseModel):
    """Represents whole resource policies logic, based on pydantic BaseModel.

    You should not create it in other ways than command: respo create [OPTIONS] FILENAME
    and access it in different way than RespoModel.get_repo_model()

    Examples:
        >>> respo_model = RespoModel.get_respo_model()
        <respo.core.RespoModel object>
        >>> respo_model.ROLES.DEFAULT
        "default"
        >>> respo_model.PERMS.USERS__DELTETE
        "users.delete"
        >>> "users.delete" in respo_model.PERMS
        True
        >>> "default" in respo_model.ROLES
        True
        >>> for role in respo_model.ROLES:
        >>>     ...
        >>> for perm in respo_model.PERMS:
        >>>     ...
    """

    permissions: List[DoubleDotLabel]
    principles: List[Principle] = []
    roles: List[Role]
    roles_permissions: Dict[str, List[str]] = {}
    ROLES: ROLESContainer = None  # type: ignore
    PERMS: PERMSContainer = None  # type: ignore

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **data) -> None:
        super().__init__(*args, **data)
        self.ROLES = ROLESContainer(self)
        self.PERMS = PERMSContainer(self)
        for role in self.roles:
            self.ROLES._add_item(str(role.name))
            self.roles_permissions[str(role.name)] = []
            for permission in role.permissions:
                self.roles_permissions[str(role.name)].append(str(permission))
        for permission in self.permissions:
            self.PERMS._add_item(str(permission))

    @staticmethod
    def get_respo_model() -> "RespoModel":
        """Loads respo model from already generated pickle or yml file.

        Paths to be used can be specified using environment variables or changed in respo.confg.

        Raises:
            RespoModelError: pickle file does not exist.
        """
        if not settings.config.path_bin_file.exists():
            raise exceptions.RespoModelError(
                f"Respo bin file does not exist in {settings.config.path_bin_file}."
                " Use command: respo create [OPTIONS] FILENAME"
            )
        with open(settings.config.path_bin_file, "rb") as respo_model_file:
            return pickle.load(respo_model_file)

    @pydantic.validator("permissions")
    def _permissions_are_unique_and_add_all(cls, permissions: List[DoubleDotLabel]):
        permissions_set: Set[DoubleDotLabel] = set(permissions)
        if not len(permissions) == permissions_set:
            for perm_name in permissions:
                try:
                    permissions_set.remove(perm_name)
                    pydantic.ValidationError
                except KeyError:
                    raise exceptions.RespoModelError(
                        f"('permissions','{perm_name}')|"
                        "Error in permissions section.\n  "
                        f"Found duplicates for permission: {perm_name}\n  "
                    )

        perm_collections = set(
            [PermissionLabel(name).collection for name in permissions]
        )
        for collection_name in perm_collections:
            all_perm = DoubleDotLabel(f"{collection_name}.all")
            if all_perm not in permissions_set:
                permissions.append(all_perm)

        permissions.sort()
        return permissions

    @pydantic.validator("principles")
    def _principles_are_valid_and_not_duplicate(
        cls, principles: List[Principle], values: Dict
    ):
        permissions: Optional[List[DoubleDotLabel]] = values.get("permissions")
        assert permissions is not None

        principles_set: Set[DoubleDotLabel] = set()
        for principle in principles:
            if principle.when not in permissions:
                raise exceptions.RespoModelError(
                    f"('principles','{principle.when}','when')|"
                    "Error in Principles section.\n  "
                    f"Permission 'when' does not exist in permissions section: {principle.when}\n  "
                )
            if principle.when in principles_set:
                raise exceptions.RespoModelError(
                    f"('principles','{principle.when}','when')|"
                    "Error in Principles section.\n  "
                    f"Permission 'when' declared multiple times: {principle.when}\n  "
                )
            principles_set.add(principle.when)

            then_permission_set: Set[DoubleDotLabel] = set()
            for then_permission in principle.then:
                if then_permission not in permissions:
                    raise exceptions.RespoModelError(
                        f"('principles','{principle.when}','then','{then_permission}')|"
                        "Error in principles section.\n  "
                        f"Error in 'then' section in principle for permission: {principle.when}\n  "
                        f"Permission does not exist in permissions section: {then_permission}\n  "
                    )
                if then_permission in then_permission_set:
                    raise exceptions.RespoModelError(
                        f"('principles','{principle.when}','then','{then_permission}')|"
                        "Error in principles section.\n  "
                        f"Error in 'then' section in principle for permission: {principle.when}\n  "
                        f"Permission declared multiple times: {then_permission}\n  "
                    )
                then_permission_set.add(then_permission)
        return principles

    @pydantic.validator("roles")
    def _roles_are_valid_and_not_duplicated(cls, roles: List[Role], values: Dict):
        permissions: Optional[List[DoubleDotLabel]] = values.get("permissions")
        assert permissions is not None

        roles_include_map: Dict[SingleLabel, List[SingleLabel]] = {}
        for role in roles:
            if role.name in roles_include_map:
                raise exceptions.RespoModelError(
                    f"('roles','{role.name}')|"
                    "Error in Roles section.\n  "
                    f"Role 'name' declared multiple times: {role.name}\n  "
                )
            if role.include is None:
                roles_include_map[role.name] = []
            else:
                roles_include_map[role.name] = role.include

            role_permission_set: Set[DoubleDotLabel] = set()
            for role_permission in role.permissions:
                if role_permission not in permissions:
                    raise exceptions.RespoModelError(
                        f"('roles','{role.name}','permissions','{role_permission}')|"
                        "Error in Roles section.\n  "
                        f"Error in 'permissions' section in role: {role.name}\n  "
                        f"Permission does not exist in permissions section: {role_permission}\n  "
                    )
                if role_permission in role_permission_set:
                    raise exceptions.RespoModelError(
                        f"('roles','{role.name}','permissions','{role_permission}')|"
                        "Error in Roles section.\n  "
                        f"Error in 'permissions' section in role: {role.name}\n  "
                        f"Permission declared multiple times: {role_permission}\n  "
                    )
                role_permission_set.add(role_permission)

        for role_name, included_role_names in roles_include_map.items():
            for included_role_name in included_role_names:
                if included_role_name not in roles_include_map:
                    raise exceptions.RespoModelError(
                        f"('roles','{role_name}','include','{included_role_name}')|"
                        "Error in Roles section.\n  "
                        f"Error in 'include' section in role: {role_name}\n  "
                        f"Included role name is not declared in Role section: {included_role_name}\n  "
                    )
                for parent_included_role_name in roles_include_map[included_role_name]:
                    if parent_included_role_name == role_name:
                        raise exceptions.RespoModelError(
                            f"('roles','{role_name}','include','{included_role_name}')|"
                            "Error in Roles section.\n  "
                            f"Error in 'include' section in two roles: {role_name},{included_role_name}\n  "
                            f"Included roles are reffering to each other, remove it from one of them\n  "
                        )
        return roles

    @pydantic.validator("roles")
    def _add_permissions_to_roles_from_included(cls, roles: List[Role]):
        for role_to_update in roles:
            if not role_to_update.include:
                continue
            for role in roles:
                if role.name not in role_to_update.include:
                    continue
                for permission in role.permissions:
                    if permission not in role_to_update.permissions:
                        role_to_update.permissions.append(permission)
        return roles

    @pydantic.validator("roles")
    def _apply_principles_section_rules_to_roles(cls, roles: List[Role], values: Dict):
        principles: Optional[List[Principle]] = values.get("principles")
        assert principles is not None

        for role in roles:
            while True:
                perms_after_resolve: List[DoubleDotLabel] = []
                for permission in role.permissions:
                    perms_after_resolve.append(permission)
                    for principle in principles:
                        if principle.when != permission:
                            continue
                        for perm_to_add in principle.then:
                            if perm_to_add not in role.permissions:
                                perms_after_resolve.append(perm_to_add)

                if role.permissions == perms_after_resolve:
                    break
                role.permissions = perms_after_resolve
        return roles

    @pydantic.validator("roles")
    def _valid_order_of_roles(cls, roles: List[Role], values: Dict):
        def sort_role_alphabeticaly(role: Role):
            return role.name

        roles.sort(key=sort_role_alphabeticaly)

        for role in roles:
            role.permissions.sort()

        return roles
