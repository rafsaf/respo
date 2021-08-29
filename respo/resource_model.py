from pydantic import BaseModel, validator, root_validator
from typing import Dict, Literal, Optional, List, Set, Union
from respo.helpers import (
    ResourcePolicyException,
    is_label_valid,
    logger,
    named_full_label,
    named_min_label,
)
from datetime import datetime


class MetadataSection(BaseModel):
    apiVersion: str
    name: str
    created_at: Optional[str]
    last_modified: Optional[str]

    @validator("apiVersion")
    def apiVersion_must_be_v1(cls, apiVersion: str) -> str:
        if not apiVersion == "v1":
            raise ValueError(
                "Error in metadata section\n"
                "Currently supported apiVersion is only 'v1'"
            )
        return apiVersion

    @validator("created_at")
    def check_created_at(cls, created_at: str, values: Dict) -> str:
        if created_at is None:
            now = datetime.utcnow()
            logger.warning(f"'metadata.created_at' is null, {now} will be placed")
            return now.isoformat()
        else:
            try:
                datetime.fromisoformat(created_at)
            except Exception as data_error:
                logger.error(data_error)
                raise ValueError(
                    "'metadata.created_at' is invalid, place valid ISO format or "
                    "leave this field empty so it will be filled"
                )
        return created_at

    @validator("last_modified")
    def update_last_modified(cls, _) -> str:
        return datetime.utcnow().isoformat()

    class Config:
        validate_all = True


class PermissionMetadata(BaseModel):
    name: str
    label: str
    description: str

    @validator("label")
    def label_must_be_in_valid_format(cls, label: str, values: Dict[str, str]) -> str:
        if not is_label_valid(label):
            raise ValueError(
                f"\nError in permissions section\n"
                f"Permission '{values['name']}' metadata is invalid.\n"
                f"Label '{label}' must be lowercase and must not contain any whitespace\n"
            )
        return label


class PermissionResource(BaseModel):
    name: str
    label: str

    def get_label(self):
        return named_min_label(self.label)


class PermissionRule(BaseModel):
    name: str
    when: str
    then: List[str]


class Permission(BaseModel):
    metadata: PermissionMetadata
    resources: List[PermissionResource]
    rules: List[PermissionRule]

    @root_validator
    def resources_are_valid_and_unique(cls, values: Dict):
        resources_set: Set[str] = set()
        metadata: PermissionMetadata = values["metadata"]
        BASE_ERR = (
            f"\nError in permissions section\n"
            f"Permission '{metadata.name}' resources are invalid.\n"
        )

        resource: PermissionResource
        for resource in values["resources"]:
            RESOURCE_ERR = f"Resource with name '{resource.name}' is invalid\n"
            parsed_resource = resource.label.split(".")
            if not len(parsed_resource) == 2:
                raise ValueError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' must be in format 'meta_label.string'\n"
                    + f"For example 'user.read'\n"
                )
            if not (
                is_label_valid(parsed_resource[0])
                and is_label_valid(parsed_resource[1])
            ):
                raise ValueError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' must be lowercase and must not contain any whitespace\n"
                )
            if parsed_resource[0] != metadata.label:
                raise ValueError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Label '{resource.label}' must start with metadata label '{metadata.label}'\n"
                    + f"Change '{parsed_resource[0]}' to '{metadata.label}'\n"
                )
            if parsed_resource[1] in resources_set:
                raise ValueError(
                    BASE_ERR
                    + RESOURCE_ERR
                    + f"Found two resources with the same label '{parsed_resource[1]}'\n"
                )
            resources_set.add(parsed_resource[1])
        return values

    @root_validator
    def rules_are_valid(cls, values: Dict):
        resources_list: List[PermissionResource] = values["resources"]
        resources_labels: Set[str] = set(
            [resource.label for resource in resources_list]
        )
        metadata: PermissionMetadata = values["metadata"]
        BASE_ERR = (
            f"\nError in permissions section\n"
            f"Permission '{metadata.name}' resources are invalid.\n"
        )

        rule: PermissionRule
        for rule in values["rules"]:
            labels_then_set = set()
            RULE_ERR = f"Rule with name '{rule.name}' is invalid\n"

            if rule.when not in resources_labels:
                raise ValueError(
                    BASE_ERR
                    + RULE_ERR
                    + f"Rule 'when' condition '{rule.when}' not found in resources labels\n"
                )
            for label in rule.then:
                if rule.then == rule.when:
                    raise ValueError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Rule 'then' condition '{rule.then}' can't be equal to when condition\n"
                    )
                if label in labels_then_set:
                    raise ValueError(
                        BASE_ERR
                        + RULE_ERR
                        + f"Found two 'then' conditions with the same label '{rule.then}'\n"
                    )
        return values

    @validator("resources")
    def add_all_resource_if_not_exist(
        cls, resources: List[PermissionResource]
    ) -> List[PermissionResource]:
        if len(resources):
            for resource in resources:
                if resource.get_label().label == "all":
                    return resources
            metadata_label = resources[0].get_label().metadata_label
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
        resources: List[PermissionResource] = values["resources"]
        if len(resources) >= 2:
            metadata_label = resources[0].get_label().metadata_label
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
    name: str
    label: str
    description: str


class OrganizationPermissionGrant(BaseModel):
    type: Literal["Allow", "Deny"]
    label: str


class Organization(BaseModel):
    metadata: OrganizationMetadata
    permissions: List[OrganizationPermissionGrant]


class RoleMetadata(BaseModel):
    name: str
    label: str
    description: str
    organization: str


class RolePermissionGrant(BaseModel):
    type: Literal["Allow", "Deny"]
    label: str


class Role(BaseModel):
    metadata: RoleMetadata
    permissions: List[RolePermissionGrant]


class Client(BaseModel):
    pk: List[str]
    organization: List[str]
    role: List[str]

    @validator("*", pre=True)
    def validate_pk(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v


class ResourceModel(BaseModel):
    metadata: MetadataSection
    permissions: List[Permission]
    organizations: List[Organization]
    roles: List[Role]

    def _label_resource_exists(self, label: str) -> bool:
        lt = named_full_label(label)
        for permission in self.permissions:
            if permission.metadata.label == lt.metadata_label:
                for resource in permission.resources:
                    if resource.label == f"{lt.metadata_label}.{lt.label}":
                        return True
        raise ResourcePolicyException(
            f"Permissions resource label {label} is not defined"
        )

    def check(self, label: str, client: Client) -> bool:
        self._label_resource_exists(label)
        for client_role in client.role:
            for role in self.roles:
                if not role.metadata.label == client_role:
                    continue
                else:
                    for permission in role.permissions:
                        if permission.label == label:
                            logger.warning("success")

                            return True
        logger.warning("fail")
        return False
