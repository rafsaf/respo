import copy
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set

from pydantic import ValidationError, validator

from respo.helpers import (
    GENERAL_ERROR_MESSAGE,
    BaseModel,
    DoubleLabel,
    RespoException,
    TripleLabel,
    is_valid_lowercase,
)

from pathlib import Path
import pickle

from respo.config import config


class T:
    def __init__(self) -> None:
        pass


class MetadataSection(BaseModel):
    name: str
    created_at: Optional[str] = None
    last_modified: Optional[str] = None

    @validator("created_at")
    def check_created_at(cls, created_at: str) -> str:
        if created_at is None:
            now = datetime.utcnow()
            return now.isoformat()
        else:
            try:
                datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
            except (ValueError, TypeError):
                raise RespoException(
                    "'metadata.created_at' is invalid, place valid ISO format (UTC) or "
                    "leave this field empty so it will be filled\n  "
                )
            return created_at

    @validator("last_modified")
    def update_last_modified(cls, _) -> str:
        return datetime.utcnow().isoformat()

    class Config:
        validate_all = True


class PermissionMetadata(BaseModel):
    name: Optional[str] = None
    label: str
    description: Optional[str] = None

    @validator("label")
    def label_must_be_in_valid_format(cls, label: str) -> str:
        if not is_valid_lowercase(label):
            raise RespoException(
                f"Error in permissions section\n  "
                f"Permission '{label}' metadata is invalid.\n  "
                f"Label '{label}' must be lowercase and must not contain any whitespace\n  "
            )
        return label


class PermissionResource(BaseModel):
    name: Optional[str] = None
    label: str

    def get_label(self):
        return DoubleLabel(full_label=self.label)


class PermissionRule(BaseModel):
    name: Optional[str] = None
    when: str
    then: List[str]


class Permission(BaseModel):
    metadata: PermissionMetadata
    resources: List[PermissionResource]
    rules: List[PermissionRule]

    @validator("resources")
    def resources_are_valid_and_unique(
        cls, resources: List[PermissionResource], values: Dict
    ):
        resources_set: Set[str] = set()
        metadata: Optional[PermissionMetadata] = values.get("metadata")
        assert metadata is not None, "General error message due to another exceptione"

        BASE_ERR = (
            f"Error in permissions section\n  "
            f"Permission '{metadata.label}' resources are invalid.\n  "
        )

        resource: PermissionResource
        for resource in resources:
            RESOURCE_ERR = f"Resource with label '{resource.label}' is invalid\n  "
            try:
                double_label = DoubleLabel(full_label=resource.label)
            except ValidationError as exc:
                raise RespoException(BASE_ERR + RESOURCE_ERR + str(exc))

            if double_label.metalabel != metadata.label:
                raise RespoException(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' must start with metadata label '{metadata.label}'\n  "
                    + f"Eg. change '{double_label.metalabel}' to '{metadata.label}'\n  "
                )
            if double_label.label == "all":
                raise RespoException(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' cant contain 'all'\n  "
                    + "'all' is reserved keyword and will be auto applied\n  "
                )

            if double_label.label in resources_set:
                raise RespoException(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Found two resources with the same label '{double_label.label}'\n  "
                )
            resources_set.add(double_label.label)
        return resources

    @validator("rules")
    def rules_are_valid(cls, rules: List[PermissionRule], values: Dict):
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
                raise RespoException(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' not found in resources labels\n  "
                )
            if DoubleLabel(full_label=rule.when).label == "all":
                raise RespoException(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' cant contain 'all'\n  "
                    + "'all' is reserved keyword and will be auto applied\n  "
                )
            for label in rule.then:
                if DoubleLabel(full_label=label).label == "all":
                    raise RespoException(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' cant contain 'all'\n  "
                        + "'all' is reserved keyword and will be auto applied\n  "
                    )
                if label == rule.when:
                    raise RespoException(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' can't be equal to when condition\n  "
                    )
                if label in labels_then_set:
                    raise RespoException(
                        BASE_ERR
                        + RULE_ERR
                        + f"Found two 'then' conditions with the same label '{label}'\n  "
                    )
                labels_then_set.add(label)
        return rules

    @validator("resources")
    def add_all_resource(
        cls, resources: List[PermissionResource]
    ) -> List[PermissionResource]:
        if len(resources):
            metadata_label = resources[0].get_label().metalabel
            resources.append(
                PermissionResource(
                    name=f"auto {metadata_label}.all", label=f"{metadata_label}.all"
                )
            )
        return resources

    @validator("rules")
    def add_all_rule_if_not_exist(
        cls, rules: List[PermissionRule], values: Dict
    ) -> List[PermissionRule]:
        resources: Optional[List[PermissionResource]] = values.get("resources")
        assert resources is not None, GENERAL_ERROR_MESSAGE

        if len(resources):
            metadata_label = resources[0].get_label().metalabel
            new_then_list = []
            for resource in resources:
                new_then_list.append(resource.label)

            rules.append(
                PermissionRule(
                    name=f"auto {metadata_label}.all",
                    when=f"{metadata_label}.all",
                    then=new_then_list,
                )
            )
        return rules


class OrganizationMetadata(BaseModel):
    name: Optional[str] = None
    label: str
    description: Optional[str] = None

    @validator("label")
    def label_must_be_in_valid_format(cls, label: str) -> str:
        if not is_valid_lowercase(label):
            raise RespoException(
                f"Error in organizations section\n  "
                f"Organization '{label}' metadata is invalid.\n  "
                f"Label '{label}' must be lowercase and must not contain any whitespace\n  "
            )
        return label

    def label_to_attribute_name(self):
        return self.label.upper()


class OrganizationPermissionGrant(BaseModel):
    type: str = "Allow"
    label: str

    @validator("type")
    def type_must_be_allow_or_deny(cls, type_str: str) -> str:
        if type_str not in ["Allow", "Deny"]:
            raise RespoException(
                f"Permission type must be literal 'Allow' or 'Deny'\n  "
                f"Currently it is {type_str}"
            )
        return type_str

    def label_to_attribute_name(self):
        return self.label.replace(".", "__").upper()


class Organization(BaseModel):
    metadata: OrganizationMetadata
    permissions: List[OrganizationPermissionGrant]

    def __str__(self) -> str:
        return self.metadata.label


class RoleMetadata(BaseModel):
    name: Optional[str] = None
    label: str
    description: Optional[str] = None
    organization: str

    @validator("label")
    def label_must_be_in_valid_format(cls, label: str) -> str:
        if not is_valid_lowercase(label):
            raise RespoException(
                f"Error in roles section\n  "
                f"Role '{label}' metadata is invalid.\n  "
                f"Label '{label}' must be lowercase and must not contain any whitespace\n  "
            )
        return label

    @property
    def full_label(self):
        return f"{self.organization}.{self.label}"

    def full_label_to_attribute_name(self):
        return self.full_label.replace(".", "__").upper()


class RolePermissionGrant(BaseModel):
    type: str = "Allow"
    label: str

    @validator("type")
    def type_must_be_allow_or_deny(cls, type_str: str) -> str:
        if type_str not in ["Allow", "Deny"]:
            raise RespoException(
                f"Permission type must be literal 'Allow' or 'Deny'\n  "
                f"Currently it is {type_str}"
            )
        return type_str


class Role(BaseModel):
    metadata: RoleMetadata
    permissions: List[RolePermissionGrant]

    def __str__(self) -> str:
        return self.metadata.full_label


class BaseRespoModel(BaseModel):
    metadata: MetadataSection
    permissions: List[Permission]
    organizations: List[Organization]
    roles: List[Role]
    permission_to_role_dict: Dict[str, Set[str]] = {}
    permission_to_organization_dict: Dict[str, Set[str]] = {}
    ORGS: T = T()
    ROLES: T = T()
    PERMS: T = T()

    class Config:
        validate_all = True
        arbitrary_types_allowed = True

    def __init__(self, *args, **data):
        super().__init__(*args, **data)

        for organization in self.organizations:
            setattr(
                self.ORGS,
                organization.metadata.label_to_attribute_name(),
                organization,
            )
            for org_permission in organization.permissions:
                setattr(
                    self.PERMS,
                    org_permission.label_to_attribute_name(),
                    org_permission.label,
                )
        for role in self.roles:
            setattr(
                self.ROLES,
                role.metadata.full_label_to_attribute_name(),
                role,
            )

    @staticmethod
    def get_respo_model() -> "BaseRespoModel":
        if not Path(
            f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}"
        ).exists():
            raise RespoException(
                f"{config.RESPO_AUTO_BINARY_FILE_NAME} file does not exist. Did you forget to create it?"
            )
        with open(
            f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}",
            "rb",
        ) as respo_model_file:
            model = pickle.load(respo_model_file)
        return model

    @classmethod
    def dict_label_to_resources(
        cls, permissions: List[Permission]
    ) -> Dict[str, List[PermissionResource]]:
        result_dict = {}
        for permission in permissions:
            result_dict[permission.metadata.label] = permission.resources
        return result_dict

    @classmethod
    def dict_label_to_rules(
        cls, permissions: List[Permission]
    ) -> Dict[str, List[PermissionRule]]:
        result_dict = {}
        for permission in permissions:
            result_dict[permission.metadata.label] = permission.rules
        return result_dict

    @validator("permissions")
    def permissions_every_metadata_is_unique_and_valid(
        cls, permissions: List[Organization]
    ):
        permission_names: Set[str] = set()
        for permission in permissions:
            if permission.metadata.label in permission_names:
                raise RespoException(
                    f"Error in permissions section\n  "
                    f"Permission '{permission.metadata.label}' metadata is invalid.\n  "
                    f"Found two permissions with the same label {permission.metadata.label}\n  "
                )
            permission_names.add(permission.metadata.label)
        return permissions

    @validator("organizations")
    def organization_every_metadata_is_unique_and_valid(
        cls, organizations: List[Organization]
    ):
        organization_names: Set[str] = set()
        for organization in organizations:
            if organization.metadata.label in organization_names:
                raise RespoException(
                    f"Error in organizations section\n  "
                    f"Organization '{organization.metadata.label}' metadata is invalid.\n  "
                    f"Found two organizations with the same label {organization.metadata.label}\n  "
                )
            organization_names.add(organization.metadata.label)
        return organizations

    @validator("organizations")
    def organization_every_permission_exists_and_can_be_applied(
        cls, organizations: List[Organization], values: Dict
    ):

        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE

        label_to_resources = cls.dict_label_to_resources(permissions)
        for organization in organizations:
            BASE_ERR = (
                f"Error in organizations section\n  "
                f"Organization '{organization.metadata.label}' permissions are invalid.\n  "
            )
            for organization_permission in organization.permissions:
                PERM_ERR = f"Permission with label '{organization_permission.label}' is invalid\n  "
                triple_label = TripleLabel(full_label=organization_permission.label)
                if triple_label.organization != organization.metadata.label:
                    raise RespoException(
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
                    raise RespoException(
                        BASE_ERR
                        + PERM_ERR
                        + f"Permission '{triple_label.to_double_label()}' not found\n  "
                    )
        return organizations

    @validator("organizations")
    def organization_resolve_complex_allow_deny_rules(
        cls, organizations: List[Organization], values: Dict
    ):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_rules = cls.dict_label_to_rules(permissions)
        while True:
            organizations_after_resolving: List[Organization] = []
            for old_organization in organizations:
                organization = copy.deepcopy(old_organization)
                for organization_permission in organization.permissions:
                    triple_label = TripleLabel(full_label=organization_permission.label)
                    for rule in label_to_rules[triple_label.metalabel]:
                        if rule.when != triple_label.to_double_label():
                            continue
                        for rule_then in rule.then:
                            new_label = f"{organization.metadata.label}.{rule_then}"
                            grant = OrganizationPermissionGrant(
                                type=organization_permission.type,
                                label=new_label,
                            )
                            if grant not in organization.permissions:
                                organization.permissions.append(grant)
                organizations_after_resolving.append(organization)

            if organizations == organizations_after_resolving:
                # no more nested rules will be found
                break
            else:
                # will look up again for nested rules
                organizations = organizations_after_resolving
        return organizations

    @validator("organizations")
    def organization_remove_all_deny_rules(cls, organizations: List[Organization]):
        new_organizations: List[Organization] = []
        for organization in organizations:
            result_permissions: List[OrganizationPermissionGrant] = []
            allow_set: Set[str] = set()
            deny_set: Set[str] = set()
            for organization_permission in organization.permissions:
                if organization_permission.type == "Allow":
                    allow_set.add(organization_permission.label)
                else:
                    deny_set.add(organization_permission.label)
            new_allow_set = allow_set - deny_set
            for label in new_allow_set:
                result_permissions.append(
                    OrganizationPermissionGrant(type="Allow", label=label)
                )
            organization.permissions = result_permissions
            new_organizations.append(organization)
        return organizations

    @validator("roles")
    def roles_every_metadata_is_unique_and_valid(cls, roles: List[Role], values: Dict):
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
            if role.metadata.label == f"root":
                raise RespoException(
                    BASE_ERR + "'root' is reserved keyword and will be auto applied\n  "
                )
            if role.metadata.organization not in organization_names:
                raise RespoException(
                    BASE_ERR
                    + f"Role's declared organization {role.metadata.organization} is invalid"
                    + f"'{role.metadata.organization}' not found\n  "
                )
            if role.metadata.label in roles_names:
                raise RespoException(
                    BASE_ERR
                    + f"Found two roles with the same label '{role.metadata.label}'\n  "
                )
            roles_names.add(role.metadata.label)
        return roles

    @validator("roles")
    def roles_every_permission_exists_and_can_be_applied(
        cls, roles: List[Role], values: Dict
    ):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_resources = cls.dict_label_to_resources(permissions)
        for role in roles:
            BASE_ERR = (
                f"Error in roles section\n  "
                f"Role '{role.metadata.label}' permissions are invalid.\n  "
            )
            for role_permission in role.permissions:
                PERM_ERR = (
                    f"Permission with label '{role_permission.label}' is invalid\n  "
                )
                triple_label = TripleLabel(full_label=role_permission.label)
                if triple_label.organization != role.metadata.organization:
                    raise RespoException(
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
                    raise RespoException(
                        BASE_ERR
                        + PERM_ERR
                        + f"Permission '{triple_label.to_double_label()}' not found\n  "
                    )
        return roles

    @validator("roles")
    def roles_resolve_complex_allow_deny_rules(cls, roles: List[Role], values: Dict):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE
        label_to_rules = cls.dict_label_to_rules(permissions)
        while True:
            roles_after_resolving: List[Role] = []
            for old_role in roles:
                role = copy.deepcopy(old_role)
                for role_permission in role.permissions:
                    triple_label = TripleLabel(full_label=role_permission.label)
                    for rule in label_to_rules[triple_label.metalabel]:
                        if rule.when != triple_label.to_double_label():
                            continue
                        for rule_then in rule.then:
                            new_label = f"{role.metadata.organization}.{rule_then}"
                            grant = RolePermissionGrant(
                                type=role_permission.type,
                                label=new_label,
                            )
                            if grant not in role.permissions:
                                role.permissions.append(grant)
                roles_after_resolving.append(role)
            if roles == roles_after_resolving:
                # no more nested rules will be found
                break
            else:
                # will look up again for nested rules
                roles = roles_after_resolving
        return roles

    @validator("roles")
    def roles_remove_all_deny_rules(cls, roles: List[Role]):
        new_roles: List[Role] = []
        for role in roles:
            result_permissions: List[RolePermissionGrant] = []
            allow_set: Set[str] = set()
            deny_set: Set[str] = set()
            for role_permission in role.permissions:
                if role_permission.type == "Allow":
                    allow_set.add(role_permission.label)
                else:
                    deny_set.add(role_permission.label)
            new_allow_set = allow_set - deny_set
            for label in new_allow_set:
                result_permissions.append(
                    RolePermissionGrant(type="Allow", label=label)
                )
            role.permissions = result_permissions
            new_roles.append(role)
        return roles

    @validator("roles")
    def add_root_role_to_every_organization(cls, roles: List[Role], values: Dict):
        organizations: Optional[List[Organization]] = values.get("organizations")
        assert organizations is not None, GENERAL_ERROR_MESSAGE
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, GENERAL_ERROR_MESSAGE

        for organization in organizations:
            role_metadata = RoleMetadata(
                organization=organization.metadata.label,
                label=f"root",
            )
            root_role = Role(metadata=role_metadata, permissions=[])
            for permission in permissions:
                for resource in permission.resources:
                    root_role.permissions.append(
                        RolePermissionGrant(
                            label=f"{organization.metadata.label}.{resource.label}"
                        )
                    )
            roles.append(root_role)
        return roles

    @validator("permission_to_role_dict")
    def creating_permission_to_role_dict_for_extra_fast_checking_permissions(
        cls, permission_to_role_dict: Dict[str, Set[str]], values: Dict
    ):
        permission_to_role_dict = defaultdict(set)
        roles: Optional[List[Role]] = values.get("roles")
        assert roles is not None, GENERAL_ERROR_MESSAGE

        for role in roles:
            for permission in role.permissions:
                permission_to_role_dict[
                    f"{role.metadata.organization}.{role.metadata.label}.{permission.label}"
                ].add(f"{role.metadata.organization}.{role.metadata.label}")
        return permission_to_role_dict

    @validator("permission_to_organization_dict")
    def creating_permission_to_organization_dict_for_extra_fast_checking_permissions(
        cls, permission_to_organization_dict: Dict[str, Set[str]], values: Dict
    ):
        permission_to_organization_dict = defaultdict(set)
        organizations: Optional[List[Organization]] = values.get("organizations")
        assert organizations is not None, GENERAL_ERROR_MESSAGE

        for organization in organizations:
            for permission in organization.permissions:
                permission_to_organization_dict[permission.label].add(
                    organization.metadata.label
                )
        return permission_to_organization_dict

    def organization_exists(self, organization_name: str) -> bool:
        for organization in self.organizations:
            if organization_name == organization.metadata.label:
                return True
        return False

    def role_exists(self, role_name: str, organization_name: str) -> bool:
        for role in self.roles:
            if (
                role.metadata.label == role_name
                and role.metadata.organization == organization_name
            ):
                return True
        return False
