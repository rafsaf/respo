from typing import Tuple

import pytest
from pydantic import ValidationError
from respo.helpers import *
from respo.helpers import _contains_whitespace

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
    ("bar.read", True),
    ("bar2.read_5", True),
]


@pytest.mark.parametrize("case", double_label_cases)
def test_double_label(case: Tuple[str, bool]):
    if case[1] is False:
        with pytest.raises(ValidationError):
            DoubleLabel(full_label=case[0])
    else:
        double_label = DoubleLabel(full_label=case[0])
        assert double_label.metalabel == double_label.full_label.split(".")[0]
        assert double_label.label == double_label.full_label.split(".")[1]
        assert double_label.full_label == case[0]


triple_label_cases = [
    ("bar.read", False),
    ("foo.bar.read ", False),
    (" foo.bar.read", False),
    ("foo.bar .read", False),
    ("foo.bar. read", False),
    ("foo.bar.read.x", False),
    ("foo .bar.read.", False),
    ("foo.foo2.bar.read", False),
    ("foo.bar.read", True),
    ("foo1.bar2.read_2", True),
]


@pytest.mark.parametrize("case", triple_label_cases)
def test_triple_label(case: Tuple[str, bool]):
    if case[1] is False:
        with pytest.raises(ValidationError):
            TripleLabel(full_label=case[0])
    else:
        triple_label = TripleLabel(full_label=case[0])
        assert triple_label.metalabel == triple_label.full_label.split(".")[1]
        assert triple_label.label == triple_label.full_label.split(".")[2]
        assert triple_label.organization == triple_label.full_label.split(".")[0]
        assert triple_label.full_label == case[0]