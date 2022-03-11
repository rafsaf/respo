import copy
import pickle
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Union

from pydantic import ValidationError, validator, Field, ConstrainedStr

from respo.config import config
import re
from typing import Dict

import ujson
from pydantic import BaseModel as PydanticRawBaseModel
from pydantic import validator

GENERAL_ERROR_MESSAGE = "Raised directly by above exception"

SINGLE_LABEL_REGEX = re.compile(r"^[a-z_]*")
DOUBLE_LABEL_REGEX = re.compile(r"^[a-z_]*.[a-z_]*")
TRIPLE_LABEL_REGEX = re.compile(r"^[a-z_]*.[a-z_]*.[a-z_]*")


class RespoError(ValueError):
    pass


class BaseModel(PydanticRawBaseModel):
    class Config:
        json_loads = ujson.loads
        json_dumps = ujson.dumps


class SingleLabel(ConstrainedStr):
    regex = SINGLE_LABEL_REGEX
    min_length = 1
    max_length = 128


class DoubleDotLabel(ConstrainedStr):
    regex = DOUBLE_LABEL_REGEX
    min_length = 3
    max_length = 128


class TripleDotLabel(ConstrainedStr):
    regex = TRIPLE_LABEL_REGEX
    min_length = 5
    max_length = 128


class TripleLabel:
    def __init__(self, full_label: Union[str, TripleDotLabel]) -> None:
        full_label_split = full_label.split(".")
        self.full_label = full_label
        self.organization = full_label_split[0]
        self.metalabel = full_label_split[1]
        self.label = full_label_split[2]

    def to_double_label(self):
        return f"{self.metalabel}.{self.label}"


class AttributesContainer:
    def __init__(self) -> None:
        self.mapping: Dict[str, Union[str, Organization, Role]] = {}

    def add_item(self, key: str, value: Union[str, "Organization", "Role"]) -> None:
        if not key.isupper():
            raise ValueError(f"Key must be uppercase: {key}")
        if not isinstance(value, (str, Organization, Role)):
            raise ValueError(
                f"Invalid type of value (possible: str, Organization, Role): {value}"
            )
        self.mapping[key] = value

    def __getattr__(self, name: str) -> Union[str, "Organization", "Role"]:
        if name.isupper():
            return self.mapping[name]
        raise AttributeError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributesContainer):
            raise ValueError(f"Cannot compare with AttributesContainer: {other}")
        return self.mapping == other.mapping


class MetadataSection(BaseModel):
    name: SingleLabel
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
                raise RespoError(
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
    label: SingleLabel


class PermissionResource(BaseModel):
    label: DoubleDotLabel


class PermissionRule(BaseModel):
    when: DoubleDotLabel
    then: List[DoubleDotLabel]


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
            metalabel = resource.label.split(".")[0]
            perm_name = resource.label.split(".")[1]
            if metalabel != metadata.label:
                raise RespoError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' must start with metadata label '{metadata.label}'\n  "
                    + f"Eg. change '{metalabel}' to '{metadata.label}'\n  "
                )
            if perm_name == "all":
                raise RespoError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' cant contain 'all'\n  "
                    + "'all' is reserved keyword and will be auto applied\n  "
                )

            if perm_name in resources_set:
                raise RespoError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Found two resources with the same label '{perm_name}'\n  "
                )
            resources_set.add(perm_name)
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
                raise RespoError(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' not found in resources labels\n  "
                )
            perm_name = rule.when.split(".")[1]
            if perm_name == "all":
                raise RespoError(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' cant contain 'all'\n  "
                    + "'all' is reserved keyword and will be auto applied\n  "
                )
            for label in rule.then:
                if perm_name == label.split(".")[1]:
                    raise RespoError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' cant contain 'all'\n  "
                        + "'all' is reserved keyword and will be auto applied\n  "
                    )
                if label == rule.when:
                    raise RespoError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{label}' can't be equal to when condition\n  "
                    )
                if label in labels_then_set:
                    raise RespoError(
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
            metadata_label = resources[0].label.split(".")[0]
            resources.append(
                PermissionResource(label=DoubleDotLabel(f"{metadata_label}.all"))
            )
        return resources

    @validator("rules")
    def add_all_rule_if_not_exist(
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
    permissions: List[OrganizationPermissionGrant]

    def __str__(self) -> str:
        return self.metadata.label


class RoleMetadata(BaseModel):
    label: SingleLabel
    organization: SingleLabel

    @property
    def full_label(self):
        return f"{self.organization}.{self.label}"

    def full_label_to_attribute_name(self):
        return self.full_label.replace(".", "__").upper()


class RolePermissionGrant(BaseModel):
    type: Literal["allow", "deny"] = "allow"
    label: TripleDotLabel


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
    ORGS: AttributesContainer = AttributesContainer()
    ROLES: AttributesContainer = AttributesContainer()
    PERMS: AttributesContainer = AttributesContainer()

    class Config:
        validate_all = True
        arbitrary_types_allowed = True

    def __init__(self, *args, **data):
        super().__init__(*args, **data)

        for organization in self.organizations:
            self.ORGS.add_item(
                organization.metadata.label_to_attribute_name(), organization
            )
            for org_permission in organization.permissions:
                self.PERMS.add_item(
                    org_permission.label_to_attribute_name(), org_permission.label
                )
        for role in self.roles:
            self.ROLES.add_item(role.metadata.full_label_to_attribute_name(), role)

    @staticmethod
    def get_respo_model() -> "BaseRespoModel":
        if not Path(
            f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}"
        ).exists():
            raise RespoError(
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
                raise RespoError(
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
                raise RespoError(
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
                    raise RespoError(
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
                    raise RespoError(
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
                            new_label = TripleDotLabel(
                                f"{organization.metadata.label}.{rule_then}"
                            )
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
            if role.metadata.label == "root":
                raise RespoError(
                    BASE_ERR + "'root' is reserved keyword and will be auto applied\n  "
                )
            if role.metadata.organization not in organization_names:
                raise RespoError(
                    BASE_ERR
                    + f"Role's declared organization {role.metadata.organization} is invalid"
                    + f"'{role.metadata.organization}' not found\n  "
                )
            if role.metadata.label in roles_names:
                raise RespoError(
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
                    raise RespoError(
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
                    raise RespoError(
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
                                label=TripleDotLabel(new_label),
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
                if role_permission.type == "allow":
                    allow_set.add(role_permission.label)
                else:
                    deny_set.add(role_permission.label)
            new_allow_set = allow_set - deny_set
            for label in new_allow_set:
                result_permissions.append(
                    RolePermissionGrant(type="allow", label=TripleDotLabel(label))
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
                label=SingleLabel("root"),
            )
            root_role = Role(metadata=role_metadata, permissions=[])
            for permission in permissions:
                for resource in permission.resources:
                    root_role.permissions.append(
                        RolePermissionGrant(
                            label=TripleDotLabel(
                                f"{organization.metadata.label}.{resource.label}"
                            )
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
                permission_to_role_dict[permission.label].add(
                    f"{role.metadata.organization}.{role.metadata.label}"
                )
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
