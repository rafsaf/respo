import string
from typing import Dict

import ujson
from pydantic import BaseModel as PydanticRawBaseModel
from pydantic import validator

GENERAL_ERROR_MESSAGE = "General error message due to another exception"


class BaseModel(PydanticRawBaseModel):
    class Config:
        json_loads = ujson.loads
        json_dumps = ujson.dumps


class RespoException(ValueError):
    pass


def _contains_whitespace(s: str) -> bool:
    for c in s:
        if c in string.whitespace:
            return True
    return False


def is_valid_lowercase(s: str) -> bool:
    if _contains_whitespace(s) or not s.islower():
        return False
    return True


class TripleLabel(BaseModel):
    organization: str = ""
    metalabel: str = ""
    label: str = ""
    full_label: str

    def to_double_label(self) -> str:
        return f"{self.metalabel}.{self.label}"

    @validator("full_label")
    def triple_label_is_correct(cls, label: str, values: Dict) -> str:
        label_list = label.split(".")
        if len(label_list) != 3:
            raise RespoException(
                f"Label {label} is not valid, use syntax 'organization.foo.read'\n  "
            )
        for label_part in label_list:
            if not is_valid_lowercase(label_part):
                raise RespoException(
                    f"Label {label} is not valid, use syntax 'organization.foo.read'\n  "
                )
        values["organization"] = label_list[0]
        values["metalabel"] = label_list[1]
        values["label"] = label_list[2]
        return label


class DoubleLabel(BaseModel):
    metalabel: str = ""
    label: str = ""
    full_label: str

    @validator("full_label")
    def double_label_is_correct(cls, label: str, values: Dict) -> str:
        label_list = label.split(".")
        if len(label_list) != 2:
            raise RespoException(
                f"Label {label} is not valid, use syntax 'foo.read'\n  "
            )
        for label_part in label_list:
            if not is_valid_lowercase(label_part):
                raise RespoException(
                    f"Label {label} is not valid, use syntax 'foo.read'\n  "
                )
        values["metalabel"] = label_list[0]
        values["label"] = label_list[1]
        return label


class RoleLabel(BaseModel):
    organization: str = ""
    role: str = ""
    full_label: str

    @validator("full_label")
    def double_label_is_correct(cls, label: str, values: Dict) -> str:
        label_list = label.split(".")
        if len(label_list) != 2:
            raise RespoException(
                f"Role label {label} is not valid, use syntax 'organization.role'\n  "
            )
        for label_part in label_list:
            if not is_valid_lowercase(label_part):
                raise RespoException(
                    f"Role label {label} is not valid, use syntax 'organization.role'\n  "
                )
        values["organization"] = label_list[0]
        values["role"] = label_list[1]
        return label
