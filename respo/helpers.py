import logging
import string
from logging import getLogger

from pydantic import BaseModel, validator


def get_logger():
    logging.basicConfig(format="%(levelname)s - %(message)s")
    logger = getLogger()
    return logger


logger = get_logger()


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
    full_label: str

    @property
    def organization(self) -> str:
        return self.full_label.split(".")[0]

    @property
    def metalabel(self) -> str:
        return self.full_label.split(".")[1]

    @property
    def label(self) -> str:
        return self.full_label.split(".")[2]

    def to_double_label(self) -> str:
        return f"{self.metalabel}.{self.label}"

    @validator("full_label")
    def triple_label_is_correct(cls, label: str) -> str:
        label_list = label.split(".")
        for label_part in label_list:
            if not is_valid_lowercase(label_part):
                raise RespoException(
                    f"Label {label} is not valid\n  "
                    "Use syntax 'organization.foo.read'\n  "
                )
        if len(label_list) == 3:
            return label
        else:
            raise RespoException(
                f"Label {label} is not valid\n  "
                "Use syntax 'organization.foo.read'\n  "
            )


class DobuelLabel(BaseModel):
    full_label: str

    @property
    def metalabel(self) -> str:
        return self.full_label.split(".")[0]

    @property
    def label(self) -> str:
        return self.full_label.split(".")[0]

    @validator("full_label")
    def double_label_is_correct(cls, label: str) -> str:
        label_list = label.split(".")
        for label_part in label_list:
            if not is_valid_lowercase(label_part):
                raise RespoException(
                    f"Label {label} is not valid\n  "
                    "Use syntax 'organization.foo.read'\n  "
                )
        if len(label_list) == 2:
            return label
        else:
            raise RespoException(
                f"Label {label} is not valid\n  Use syntax 'foo.read'\n  "
            )
