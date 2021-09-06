from datetime import datetime
from typing import Dict, List, Literal, Optional, Set

from pydantic import BaseModel, validator, ValidationError
from respo.client import Client
from respo.helpers import (
    DoubleLabel,
    RespoException,
    TripleLabel,
    is_valid_lowercase,
)


class MetadataSection(BaseModel):
    name: str
    created_at: Optional[str]
    last_modified: Optional[str]

    @validator("created_at")
    def check_created_at(cls, created_at: str) -> str:
        if created_at is None:
            now = datetime.utcnow()
            return now.isoformat()
        else:
            try:
                datetime.fromisoformat(created_at)
            except (ValueError, TypeError):
                raise RespoException(
                    "'metadata.created_at' is invalid, place valid ISO format or "
                    "leave this field empty so it will be filled\n  "
                )
            return created_at

    @validator("last_modified")
    def update_last_modified(cls, _) -> str:
        return datetime.utcnow().isoformat()

    class Config:
        validate_all = True


class PermissionMetadata(BaseModel):
    name: Optional[str]
    label: str
    description: Optional[str]

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
    name: Optional[str]
    label: str

    def get_label(self):
        return DoubleLabel(full_label=self.label)


class PermissionRule(BaseModel):
    name: Optional[str]
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
        assert (
            resources_list is not None
        ), "General error message due to another exception"

        resources_labels: Set[str] = set(
            [resource.label for resource in resources_list]
        )
        metadata: Optional[PermissionMetadata] = values.get("metadata")
        assert metadata is not None, "General error message due to another exception"

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
            for label in rule.then:
                if label == rule.when:
                    raise RespoException(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{rule.then}' can't be equal to when condition\n  "
                    )
                if label in labels_then_set:
                    raise RespoException(
                        BASE_ERR
                        + RULE_ERR
                        + f"Found two 'then' conditions with the same label '{rule.then}'\n  "
                    )
                labels_then_set.add(label)
        return rules

    @validator("resources")
    def add_all_resource_if_not_exist(
        cls, resources: List[PermissionResource]
    ) -> List[PermissionResource]:
        if len(resources):
            metadata_label = resources[0].get_label().metalabel
            for resource in resources:
                if resource.label == f"{metadata_label}.all":
                    return resources

            resources.append(
                PermissionResource(
                    name=f"{metadata_label}.all", label=f"{metadata_label}.all"
                )
            )
        return resources

    @validator("rules")
    def add_all_rule_if_not_exist(
        cls, rules: List[PermissionRule], values: Dict
    ) -> List[PermissionRule]:
        resources: Optional[List[PermissionResource]] = values.get("resources")
        assert resources is not None, "General error message due to another exception"

        if len(resources):
            metadata_label = resources[0].get_label().metalabel
            for rule in rules:
                if rule.when == f"{metadata_label}.all":
                    return rules
            new_then_list = []
            for resource in resources:
                if resource.get_label().label != "all":
                    new_then_list.append(resource.label)

            rules.append(
                PermissionRule(
                    name=f"{metadata_label}.all",
                    when=f"{metadata_label}.all",
                    then=new_then_list,
                )
            )
        return rules


class OrganizationMetadata(BaseModel):
    name: Optional[str]
    label: str
    description: Optional[str]

    @validator("label")
    def label_must_be_in_valid_format(cls, label: str) -> str:
        if not is_valid_lowercase(label):
            raise RespoException(
                f"Error in organizations section\n  "
                f"Organization '{label}' metadata is invalid.\n  "
                f"Label '{label}' must be lowercase and must not contain any whitespace\n  "
            )
        return label


class OrganizationPermissionGrant(BaseModel):
    type: Literal["Allow", "Deny"] = "Allow"
    label: str


class Organization(BaseModel):
    metadata: OrganizationMetadata
    permissions: List[OrganizationPermissionGrant]


class RoleMetadata(BaseModel):
    name: Optional[str]
    label: str
    description: Optional[str]
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


class RolePermissionGrant(BaseModel):
    type: Literal["Allow", "Deny"] = "Allow"
    label: str


class Role(BaseModel):
    metadata: RoleMetadata
    permissions: List[RolePermissionGrant]


class RespoModel(BaseModel):
    metadata: MetadataSection
    permissions: List[Permission]
    organizations: List[Organization]
    roles: List[Role]

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
        assert permissions is not None, "General error message due to another exception"

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
                        if (
                            resource.label
                            == f"{triple_label.metalabel}.{triple_label.label}"
                        ):
                            exists = True
                            break
                if not exists:
                    raise RespoException(
                        BASE_ERR
                        + PERM_ERR
                        + f"Permission '{triple_label.metalabel}.{triple_label.label}' not found\n  "
                    )
        return organizations

    @validator("organizations")
    def organization_resolve_complex_allow_deny_rules(
        cls, organizations: List[Organization], values: Dict
    ):
        permissions: Optional[List[Permission]] = values.get("permissions")
        assert permissions is not None, "General error message due to another exception"
        label_to_rules = cls.dict_label_to_rules(permissions)

        while True:
            organizations_after_resolving: List[Organization] = []
            for organization in organizations:
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
        assert (
            organizations is not None
        ), "General error message due to another exception"

        roles_names: Set[str] = set()
        organization_names: Set[str] = set()

        for organization in organizations:
            organization_names.add(organization.metadata.label)

        for role in roles:
            BASE_ERR = (
                f"Error in roles section\n  "
                f"Role '{role.metadata.label}' metadata is invalid.\n  "
            )
            if role.metadata.organization not in organization_names:
                raise RespoException(
                    BASE_ERR
                    + f"Role's declared organization "
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
        assert permissions is not None, "General error message due to another exception"
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
        assert permissions is not None, "General error message due to another exception"
        label_to_rules = cls.dict_label_to_rules(permissions)
        while True:
            roles_after_resolving: List[Role] = []
            for role in roles:
                for role_permission in role.permissions:
                    triple_label = TripleLabel(full_label=role_permission.label)
                    for rule in label_to_rules[triple_label.metalabel]:
                        if (
                            rule.when
                            != f"{triple_label.metalabel}.{triple_label.label}"
                        ):
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

    def _label_resource_exists(self, label: str) -> bool:
        triple_label = TripleLabel(full_label=label)
        for permission in self.permissions:
            if permission.metadata.label == triple_label.metalabel:
                for resource in permission.resources:
                    if (
                        resource.label
                        == f"{triple_label.metalabel}.{triple_label.label}"
                    ):
                        return True
        raise RespoException(f"Permissions resource label {label} not found\n  ")

    def _check_organization(self, label: str, organization_name: str) -> bool:
        for organization in self.organizations:
            if organization.metadata.label != organization_name:
                continue
            for permission in organization.permissions:
                if permission.label == label:
                    return True
        return False

    def check(self, label: str, client: Client, force: bool = False) -> bool:
        if not force:
            self._label_resource_exists(label)
        checked_organizations: Set[str] = set()
        for client_role in client.role:
            for role in self.roles:
                if not role.metadata.label == client_role:
                    continue
                else:
                    for permission in role.permissions:
                        if permission.label == label:
                            return True
                    if self._check_organization(label, role.metadata.organization):
                        return True
                    checked_organizations.add(role.metadata.organization)
        for organization in [
            org for org in client.organization if org not in checked_organizations
        ]:
            if self._check_organization(label, organization):
                return True

        return False
