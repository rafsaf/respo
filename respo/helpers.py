import logging
import string
from logging import getLogger
from collections import namedtuple

logging.basicConfig(format="%(levelname)s - %(message)s")
logger = getLogger()


class RespoException(Exception):
    pass


def contains_whitespace(s: str) -> bool:
    for c in s:
        if c in string.whitespace:
            return True
    return False


def is_label_valid(s: str) -> bool:
    if contains_whitespace(s) or not s.islower():
        return False
    return True


_named_min_label = namedtuple("LabelSplitMin", ["metadata_label", "label"])
_named_full_label = namedtuple(
    "LabelSplitFull", ["organization", "metadata_label", "label"]
)


def named_min_label(label: str):
    split = label.split(".")
    for s in split:
        if not is_label_valid(s):
            raise RespoException(f"Label {label} is not valid")
    if len(split) == 2:
        return _named_min_label(split[0], split[1])
    else:
        raise RespoException(f"Label {label} is not valid")


def named_full_label(label: str):
    split = label.split(".")
    for s in split:
        if not is_label_valid(s):
            raise RespoException(f"Label {label} is not valid")
    if len(split) == 3:
        return _named_full_label(split[0], split[1], split[2])
    else:
        raise RespoException(
            f"Label '{label}' is not valid\n"
            f"Hint: use syntax 'organization.meta_label.permission', eg. 'foo.user.delete'\n"
            f"For permission scoped globally use 'all.user.delete'"
        )
