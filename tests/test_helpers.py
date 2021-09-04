from typing import Tuple
from respo.helpers import _contains_whitespace
from respo.helpers import *
import pytest
from pydantic import ValidationError

test_strings = [
    ("xxx", False),
    ("xx x", True),
    ("xx\nx", True),
    ("xx\rx", True),
    ("xx\tx", True),
    (" xxx", True),
    ("xxx ", True),
]


@pytest.mark.parametrize("case", test_strings)
def test_contains_whitespace(case: Tuple[str, bool]):
    assert _contains_whitespace(case[0]) == case[1]


lowercase_test_strings = [
    ("xxx", True),
    ("xx x", False),
    ("xx\nx", False),
    ("xx\rx", False),
    ("xx\tx", False),
    (" xxx", False),
    ("xxx ", False),
    ("xxX", False),
]


@pytest.mark.parametrize("case", lowercase_test_strings)
def test_is_valid_lowercase(case: Tuple[str, bool]):
    assert is_valid_lowercase(case[0]) == case[1]


double_label_cases = [
    ("foo.bar.read", False),
    ("bar.read ", False),
    (" bar.read", False),
    ("bar .read", False),
    ("bar. read", False),
    ("bar.read.x", False),
    ("bar.read.", False),
    (".bar.read", False),
]


@pytest.mark.parametrize("case", double_label_cases)
def test_double_label(case: Tuple[str, bool]):
    with pytest.raises(ValidationError):
        DobuelLabel(full_label=case[0])


triple_label_cases = [
    ("bar.read", False),
    ("foo.bar.read ", False),
    (" foo.bar.read", False),
    ("foo.bar .read", False),
    ("foo.bar. read", False),
    ("foo.bar.read.x", False),
    ("foo .bar.read.", False),
    ("foo.foo2.bar.read", False),
]


@pytest.mark.parametrize("case", triple_label_cases)
def test_triple_label(case: Tuple[str, bool]):
    with pytest.raises(ValidationError):
        TripleLabel(full_label=case[0])
