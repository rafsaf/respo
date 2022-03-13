import collections
import copy
import datetime
import pickle
import re
from typing import Dict, Iterator, List, Literal, Optional, Set, Union

import pydantic
import ujson
import yaml

from respo import exceptions, settings

GENERAL_ERROR_MESSAGE = "Raised directly by above exception"

SINGLE_LABEL_REGEX = re.compile(r"^[a-z_0-9]*$")
DOUBLE_LABEL_REGEX = re.compile(r"^[a-z_0-9]*\.[a-z_0-9]*$")


class LabelConstrainedStr(pydantic.ConstrainedStr):
    @classmethod
    def validate(cls, value: str) -> str:
        if cls.regex:
            if cls.regex.fullmatch(value) is None:
                raise pydantic.errors.StrRegexError(pattern=cls.regex.pattern)

        return value


class SingleLabel(LabelConstrainedStr):
    regex = SINGLE_LABEL_REGEX
    min_length = 1
    max_length = 128


class DoubleDotLabel(LabelConstrainedStr):
    regex = DOUBLE_LABEL_REGEX
    min_length = 3
    max_length = 128


class BaseModel(pydantic.BaseModel):
    class Config:
        json_loads = ujson.loads
        json_dumps = ujson.dumps


class PermissionLabel:
    """Helper class for triple (permission) labels validation

    For TripleDotLabel there is no validation step as it is already validated.

    Examples:
        >>> PermissionLabel("x.y")
        OK
        >>> PermissionLabel("x")
        ValueError
    """

    def __init__(self, full_label: str) -> None:
        if DOUBLE_LABEL_REGEX.fullmatch(full_label) is None:
            raise ValueError(
                f"Permission does not match {DOUBLE_LABEL_REGEX} regex: {full_label}"
            )
        full_label_split = full_label.split(".")
        self.full_label = full_label
        self.collection = full_label_split[0]
        self.label = full_label_split[1]


class RoleLabel:
    """Helper class for double (role) labels validation

    For Role there is no validation step as it is already validated.

    Examples:
        >>> RoleLabel("x.y")
        OK
        >>> RoleLabel(respo_model.ROLES.DEFAULT__ROOT)
        OK
        >>> RoleLabel("invalid")
        ValueError
    """

    def __init__(self, full_label: Union[str, "Role"]) -> None:
        if isinstance(full_label, Role):
            self.organization = str(full_label.metadata.organization)
            self.role = str(full_label.metadata.label)
        else:
            if DOUBLE_LABEL_REGEX.fullmatch(full_label) is None:
                raise ValueError(
                    f"Label does not match {DOUBLE_LABEL_REGEX} regex: {full_label}"
                )
            full_label_split = full_label.split(".")
            self.organization = full_label_split[0]
            self.role = full_label_split[1]
        self.full_label = str(full_label)

    def __str__(self):
        return self.full_label


class OrganizationLabel:
    """Helper class for single (organization) labels validation

    For Organization there is no validation step as it is already validated.

    Examples:
        >>> PermissionLabel("organization")
        OK
        >>> PermissionLabel(respo_model.ROLES.DEFAULT)
        OK
        >>> PermissionLabel("x.y")
        ValueError
    """

    def __init__(self, full_label: Union[str, "Organization"]) -> None:
        if isinstance(full_label, Organization):
            self.organization = str(full_label.metadata.label)
        else:
            if SINGLE_LABEL_REGEX.fullmatch(full_label) is None:
                raise ValueError(
                    f"Label does not match {SINGLE_LABEL_REGEX} regex: {full_label}"
                )
            self.organization = full_label
        self.full_label = str(full_label)

    def __str__(self):
        return self.organization


class LabelsContainer:
    """Container for respo model attributes

    Stores human friendly dict with attrs in self.mapping that can be accessed via attributes.

    Examples:
        >>> attrs_container = LabelsContainer()
        >>> attrs_container._add_item("invalid", {"foo": 5})
        ValueError raised
        >>> attrs_container._add_item("MY_KEY", {"foo": 5})
        >>> attrs_container.mapping["MY_KEY"]
        {"foo": 5}
        >>> attrs_container.MY_KEY
        {"foo": 5}
    """

    def __init__(self, labels_list: List[str]) -> None:
        self.labels_list = labels_list

    def _add_item(self, label: str) -> None:
        self.__dict__[label.upper().replace(".", "__")] = label
        self.labels_list.append(label)

    def __iter__(self) -> Iterator[str]:
        return iter(self.labels_list)

    def __contains__(self, key: str) -> bool:
        return key in self.labels_list

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LabelsContainer):
            raise ValueError(f"Cannot compare to not a LabelsContainer: {other}")
        return self.labels_list == other.labels_list


class MetadataSection(BaseModel):
    name: str
    created_at: Optional[str] = None
    last_modified: Optional[str] = None

    @pydantic.validator("created_at")
    def _check_created_at(cls, created_at: str) -> str:
        if created_at is None:
            now = datetime.datetime.utcnow()
            return now.isoformat()
        else:
            try:
                datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
            except (ValueError, TypeError):
                raise exceptions.RespoModelError(
                    "'metadata.created_at' is invalid, place valid ISO format (UTC) or "
                    "leave this field empty so it will be filled\n  "
                )
            return created_at

    @pydantic.validator("last_modified")
    def _update_last_modified(cls, _) -> str:
        return datetime.datetime.utcnow().isoformat()

    class Config:
        validate_all = True


class PermissionMetadata(BaseModel):
    label: SingleLabel


class PermissionResource(BaseModel):
    label: DoubleDotLabel


class Permission(BaseModel):
    metadata: PermissionMetadata
    resources: List[PermissionResource]
    rules: List[PermissionRule]

    @pydantic.validator("rules")
    def _rules_are_valid(cls, rules: List[PermissionRule], values: Dict):
        resources_list: Optional[List[PermissionResource]] = values.get("resources")
        assert resources_list is not None, GENERAL_ERROR_MESSAGE

        resources_labels: Set[str] = set(
            [resource.label for resource in resources_list]
        )
        metadata: Optional[PermissionMetadata] = values.get("metadata")
        assert metadata is not None, GENERAL_ERROR_MESSAGE

        BASE_ERR = (
            f"Error in permissions section\n  "
            f"Permission '{metadata.label}' resources are invalid.\n  "
        )

        rule: PermissionRule
        for rule in rules:
            labels_then_set = set()
            RULE_ERR = f"Rule with when '{rule.when}' is invalid\n  "

            if rule.when not in resources_labels:
                raise exceptions.RespoModelError(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' not found in resources labels\n  "
                )
            perm_name = rule.when.split(".")[1]
            if perm_name == "all":
                raise exceptions.RespoModelError(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' cant be equal to 'all'\n  "
                    + "'all' is reserved keyword and will be auto applied\n  "
                )
            for label in rule.then:
                if label.split(".")[1] == "all":
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' cant be equal to 'all'\n  "
                        + "'all' is reserved keyword and will be auto applied\n  "
                    )
                if label == rule.when:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' can't be equal to when condition\n  "
                    )
                if label in labels_then_set:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Found two 'then' conditions with the same label '{label}'\n  "
                    )
                labels_then_set.add(label)
        return rules

    @pydantic.validator("resources")
    def _add_all_resource(
        cls, resources: List[PermissionResource]
    ) -> List[PermissionResource]:
        if len(resources):
            metadata_label = resources[0].label.split(".")[0]
            resources.append(
                PermissionResource(label=DoubleDotLabel(f"{metadata_label}.all"))
            )
        return resources

    @pydantic.validator("rules")
    def _add_all_rule_if_not_exist(
        cls, rules: List[PermissionRule], values: Dict
    ) -> List[PermissionRule]:
        resources: Optional[List[PermissionResource]] = values.get("resources")
        assert resources is not None, GENERAL_ERROR_MESSAGE

        if len(resources):
            metadata_label = resources[0].label.split(".")[0]
            new_then_list = []
            for resource in resources:
                new_then_list.append(resource.label)

            rules.append(
                PermissionRule(
                    when=DoubleDotLabel(f"{metadata_label}.all"),
                    then=new_then_list,
                )
            )
        return rules


class OrganizationMetadata(BaseModel):
    label: SingleLabel

    def label_to_attribute_name(self):
        return self.label.upper()


class OrganizationPermissionGrant(BaseModel):
    type: Literal["allow", "deny"] = "allow"
    label: TripleDotLabel

    def label_to_attribute_name(self):
        return self.label.replace(".", "__").upper()


class Organization(BaseModel):
    metadata: OrganizationMetadata
    permissions_grants: List[OrganizationPermissionGrant] = pydantic.Field(
        alias="permissions"
    )

    class Config:
        allow_population_by_field_name = True

    def __str__(self) -> str:
        return self.metadata.label


class Role(BaseModel):
    name: SingleLabel
    base_on: SingleLabel
    permissions: List[DoubleDotLabel]


class Principle(BaseModel):
    when: DoubleDotLabel
    then: List[DoubleDotLabel]


class RespoModel(BaseModel):
    """Represents whole resource policies logic, based on pydantic BaseModel.

    You should not create it in other ways than command: respo create [OPTIONS] FILENAME
    and access it in different way than RespoModel.get_repo_model()

    Examples:
        >>> respo_model = RespoModel.get_respo_model()
        <respo.core.RespoModel object>
        >>> respo_model.ROLES.DEFAULT__ROOT
        <respo.core.Role object>
        >>> str(respo_model.ROLES.DEFAULT__ROOT)
        "default.root"
        >>> respo_model.PERMS.STUDENTS__USERS__CREATE
        "students.users.create"
        >>> respo_model.ORGS.MY_ORGANIZATION
        <respo.core.Organization object>
        >>> str(respo_model.ORGS.MY_ORGANIZATION)
        "my_organization.users.create"
        >>> respo_model.organization_exists("no_such_organization")
        False
        >>> respo_model.organization_exists(respo_model.ORGS.DEFAULT)
        True
        >>> respo_model.role_exists("default.invalid_role")
        False
        >>> respo_model.role_exists("text without any sense")
        False
    """

    permissions: List[DoubleDotLabel]
    principles: List[Principle]
    roles: List[Role]
    ROLES: LabelsContainer = LabelsContainer([])
    PERMS: LabelsContainer = LabelsContainer([])

    class Config:
        validate_all = True
        arbitrary_types_allowed = True

    def __init__(self, *args, **data) -> None:
        super().__init__(*args, **data)
        for organization in self.organizations:
            for org_permission in organization.permissions_grants:
                self.PERMS._add_item(str(org_permission.label))
        for role in self.roles:
            self.ROLES._add_item(str(role.metadata.full_label))

    @pydantic.validator("permissions")
    def _check_permissions_are_unique_and_add_all_permissions(
        cls, permissions: List[DoubleDotLabel]
    ):
        permissions_set: Set[DoubleDotLabel] = set(permissions)
        if not len(permissions) == permissions_set:
            for perm_name in permissions:
                try:
                    permissions_set.remove(perm_name)
                except KeyError:
                    raise exceptions.RespoModelError(
                        "Error in permissions section.\n"
                        f"Found two permissions with the same label '{perm_name}'\n  "
                    )
        perm_collections = set(
            [PermissionLabel(name).collection for name in permissions]
        )
        for collection_name in perm_collections:
            all_perm = DoubleDotLabel(f"{collection_name}.all")
            if not all_perm in permissions_set:
                permissions.append(all_perm)
        return permissions

    @pydantic.validator("roles")
    def _check_permissions_are_unique_and_add_all_permissions(
        cls, permissions: List[DoubleDotLabel]
    ):
        permissions_set: Set[DoubleDotLabel] = set(permissions)
        if not len(permissions) == permissions_set:
            for perm_name in permissions:
                try:
                    permissions_set.remove(perm_name)
                except KeyError:
                    raise exceptions.RespoModelError(
                        "Error in permissions section.\n"
                        f"Found two permissions with the same label '{perm_name}'\n  "
                    )
        perm_collections = set(
            [PermissionLabel(name).collection for name in permissions]
        )
        for collection_name in perm_collections:
            all_perm = DoubleDotLabel(f"{collection_name}.all")
            if not all_perm in permissions_set:
                permissions.append(all_perm)
        return permissions

    @staticmethod
    def get_respo_model(yml_file: bool = False) -> "RespoModel":
        """Loads respo model from already generated pickle or yml file.

        Paths to be used can be specified using environment variables or changed in respo.confg.

        Args:
            yml_file: when True, yml file will be used instead of deafult pickled one.

        Raises:
            RespoModelError: Choosed file (yml or pickle) does not exist.
        """
        if yml_file:
            if not settings.config.path_yml_file.exists():
                raise exceptions.RespoModelError(
                    f"Respo yml file does not exist in {settings.config.path_yml_file}."
                    " Use command: respo create [OPTIONS] FILENAME"
                )
            with open(settings.config.path_yml_file, "rb") as respo_model_file:
                return yaml.load(respo_model_file, yaml.Loader)

        else:
            if not settings.config.path_bin_file.exists():
                raise exceptions.RespoModelError(
                    f"Respo bin file does not exist in {settings.config.path_bin_file}."
                    " Use command: respo create [OPTIONS] FILENAME"
                )
            with open(settings.config.path_bin_file, "rb") as respo_model_file:
                return pickle.load(respo_model_file)

    @classmethod
    def _resources_mapping(
        cls, permissions: List[Permission]
    ) -> Dict[str, List[PermissionResource]]:
        result_dict: Dict[str, List[PermissionResource]] = {}
        for permission in permissions:
            result_dict[permission.metadata.label] = permission.resources
        return result_dict

    @classmethod
    def _rules_mapping(
        cls, permissions: List[Permission]
    ) -> Dict[str, List[PermissionRule]]:
        result_dict: Dict[str, List[PermissionRule]] = {}
        for permission in permissions:
            result_dict[permission.metadata.label] = permission.rules
        return result_dict

    @pydantic.validator("permissions")
    def _permissions_every_metadata_is_unique_and_valid(
        cls, permissions: List[Organization]
    ):
        permission_names: Set[str] = set()
        for permission in permissions:
            if permission.metadata.label in permission_names:
                raise exceptions.RespoModelError(
                    f"Error in permissions section\n  "
                    f"Permission '{permission.metadata.label}' metadata is invalid.\n  "
                    f"Found two permissions with the same label {permission.metadata.label}\n  "
                )
            permission_names.add(permission.metadata.label)
        return permissions

    @pydantic.validator("organizations")
    def _organization_every_metadata_is_unique_and_valid(
        cls, organizations: List[Organization]
    ):
        organization_names: Set[str] = set()
        for organization in organizations:
            if organization.metadata.label in organization_names:
                raise exceptions.RespoModelError(
                    f"Error in organizations section\n  "
                    f"Organization '{organization.metadata.label}' metadata is invalid.\n  "
                    f"Found two organizations with the same label {organization.metadata.label}\n  "
                )
            organization_names.add(organization.metadata.label)
        return organizations

    @pydantic.validator("organizations")
    def _organization_every_permission_exists_and_can_be_applied(
        cls, organizations: List[Organization], values: Dict
    ):

        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE

        label_to_resources = cls._resources_mapping(permissions)
        for organization in organizations:
            BASE_ERR = (
                f"Error in organizations section\n  "
                f"Organization '{organization.metadata.label}' permissions are invalid.\n  "
            )
            for organization_permission in organization.permissions_grants:
                PERM_ERR = f"Permission with label '{organization_permission.label}' is invalid\n  "
                triple_label = PermissionLabel(full_label=organization_permission.label)
                if triple_label.organization != organization.metadata.label:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + PERM_ERR
                        + f"'{triple_label.organization}' must be equal to '{organization.metadata.label}'\n  "
                    )
                exists = False
                if triple_label.metalabel in label_to_resources:
                    for resource in label_to_resources[triple_label.metalabel]:
                        if resource.label == triple_label.to_double_label():
                            exists = True
                            break
                if not exists:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + PERM_ERR
                        + f"Permission '{triple_label.to_double_label()}' not found\n  "
                    )
        return organizations

    @pydantic.validator("organizations")
    def _organization_resolve_complex_allow_deny_rules(
        cls, organizations: List[Organization], values: Dict
    ):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_rules = cls._rules_mapping(permissions)
        while True:
            organizations_after_resolving: List[Organization] = []
            for old_organization in organizations:
                organization = copy.deepcopy(old_organization)
                for organization_permission in organization.permissions_grants:
                    triple_label = PermissionLabel(
                        full_label=organization_permission.label
                    )
                    for rule in label_to_rules[triple_label.metalabel]:
                        if rule.when != triple_label.to_double_label():
                            continue
                        for rule_then in rule.then:
                            new_label = TripleDotLabel(
                                f"{organization.metadata.label}.{rule_then}"
                            )
                            grant = OrganizationPermissionGrant(
                                type=organization_permission.type,
                                label=new_label,
                            )
                            if grant not in organization.permissions_grants:
                                organization.permissions_grants.append(grant)
                organizations_after_resolving.append(organization)

            if organizations == organizations_after_resolving:
                # no more nested rules will be found
                break
            else:
                # will look up again for nested rules
                organizations = organizations_after_resolving
        return organizations

    @pydantic.validator("organizations")
    def _organization_remove_all_deny_rules(cls, organizations: List[Organization]):
        new_organizations: List[Organization] = []
        for organization in organizations:
            result_permissions: List[OrganizationPermissionGrant] = []
            allow_set: Set[str] = set()
            deny_set: Set[str] = set()
            for organization_permission in organization.permissions_grants:
                if organization_permission.type == "allow":
                    allow_set.add(organization_permission.label)
                else:
                    deny_set.add(organization_permission.label)
            new_allow_set = allow_set - deny_set
            for label in new_allow_set:
                result_permissions.append(
                    OrganizationPermissionGrant(
                        type="allow", label=TripleDotLabel(label)
                    )
                )
            organization.permissions_grants = result_permissions
            new_organizations.append(organization)
        return organizations

    @pydantic.validator("roles")
    def _roles_every_metadata_is_unique_and_valid(cls, roles: List[Role], values: Dict):
        organizations: Optional[List[Organization]] = values.get("organizations")
        assert organizations is not None, GENERAL_ERROR_MESSAGE

        roles_names: Set[str] = set()
        organization_names: Set[str] = set()

        for organization in organizations:
            organization_names.add(organization.metadata.label)

        for role in roles:
            BASE_ERR = (
                f"Error in roles section\n  "
                f"Role '{role.metadata.label}' metadata is invalid.\n  "
            )
            if role.metadata.label == "root":
                raise exceptions.RespoModelError(
                    BASE_ERR + "'root' is reserved keyword and will be auto applied\n  "
                )
            if role.metadata.organization not in organization_names:
                raise exceptions.RespoModelError(
                    BASE_ERR
                    + f"Role's declared organization {role.metadata.organization} is invalid"
                    + f"'{role.metadata.organization}' not found\n  "
                )
            if role.metadata.label in roles_names:
                raise exceptions.RespoModelError(
                    BASE_ERR
                    + f"Found two roles with the same label '{role.metadata.label}'\n  "
                )
            roles_names.add(role.metadata.label)
        return roles

    @pydantic.validator("roles")
    def _roles_every_permission_exists_and_can_be_applied(
        cls, roles: List[Role], values: Dict
    ):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_resources = cls._resources_mapping(permissions)
        for role in roles:
            BASE_ERR = (
                f"Error in roles section\n  "
                f"Role '{role.metadata.label}' permissions are invalid.\n  "
            )
            for role_permission in role.permissions_grants:
                PERM_ERR = (
                    f"Permission with label '{role_permission.label}' is invalid\n  "
                )
                triple_label = PermissionLabel(full_label=role_permission.label)
                if triple_label.organization != role.metadata.organization:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + PERM_ERR
                        + f"'{triple_label.organization}' must be equal to '{role.metadata.organization}'\n  "
                    )
                exists = False
                if triple_label.metalabel in label_to_resources:
                    for resource in label_to_resources[triple_label.metalabel]:
                        if resource.label == triple_label.to_double_label():
                            exists = True
                            break
                if not exists:
                    raise exceptions.RespoModelError(
                        BASE_ERR
                        + PERM_ERR
                        + f"Permission '{triple_label.to_double_label()}' not found\n  "
                    )
        return roles

    @pydantic.validator("roles")
    def _roles_resolve_complex_allow_deny_rules(cls, roles: List[Role], values: Dict):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_rules = cls._rules_mapping(permissions)
        while True:
            roles_after_resolving: List[Role] = []
            for old_role in roles:
                role = copy.deepcopy(old_role)
                for role_permission in role.permissions_grants:
                    triple_label = PermissionLabel(full_label=role_permission.label)
                    for rule in label_to_rules[triple_label.metalabel]:
                        if rule.when != triple_label.to_double_label():
                            continue
                        for rule_then in rule.then:
                            new_label = f"{role.metadata.organization}.{rule_then}"
                            grant = RolePermissionGrant(
                                type=role_permission.type,
                                label=TripleDotLabel(new_label),
                            )
                            if grant not in role.permissions_grants:
                                role.permissions_grants.append(grant)
                roles_after_resolving.append(role)
            if roles == roles_after_resolving:
                # no more nested rules will be found
                break
            else:
                # will look up again for nested rules
                roles = roles_after_resolving
        return roles

    @pydantic.validator("roles")
    def _roles_remove_all_deny_rules(cls, roles: List[Role]):
        new_roles: List[Role] = []
        for role in roles:
            result_permissions: List[RolePermissionGrant] = []
            allow_set: Set[str] = set()
            deny_set: Set[str] = set()
            for role_permission in role.permissions_grants:
                if role_permission.type == "allow":
                    allow_set.add(role_permission.label)
                else:
                    deny_set.add(role_permission.label)
            new_allow_set = allow_set - deny_set
            for label in new_allow_set:
                result_permissions.append(
                    RolePermissionGrant(type="allow", label=TripleDotLabel(label))
                )
            role.permissions_grants = result_permissions
            new_roles.append(role)
        return roles

    @pydantic.validator("roles")
    def _add_root_role_to_every_organization(cls, roles: List[Role], values: Dict):
        organizations: Optional[List[Organization]] = values.get("organizations")
        assert organizations is not None, GENERAL_ERROR_MESSAGE
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE

        for organization in organizations:
            role_metadata = RoleMetadata(
                organization=organization.metadata.label,
                label=SingleLabel("root"),
            )
            root_role = Role(metadata=role_metadata, permissions=[])
            for permission in permissions:
                for resource in permission.resources:
                    root_role.permissions_grants.append(
                        RolePermissionGrant(
                            label=TripleDotLabel(
                                f"{organization.metadata.label}.{resource.label}"
                            )
                        )
                    )
            roles.append(root_role)
        return roles

    @pydantic.validator("roles_labels")
    def _create_roles_labels_for_fast_checking_permissions(
        cls, roles_labels: Dict[str, List[str]], values: Dict
    ) -> Dict[str, List[str]]:
        roles: Optional[List[Role]] = values.get("roles")
        assert roles is not None, GENERAL_ERROR_MESSAGE

        for role in roles:
            for permission in role.permissions_grants:
                triple_label = PermissionLabel(permission.label)
                if triple_label.to_role() in roles_labels:
                    roles_labels[triple_label.to_role()].append(triple_label.label)
                else:
                    roles_labels[triple_label.to_role()] = [triple_label.label]
        return roles_labels
