from typing import Tuple

import pytest
from pydantic import ValidationError

from respo import TripleLabel, RoleLabel

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
        with pytest.raises(ValueError):
            RoleLabel(full_label=case[0])
    else:
        double_label = RoleLabel(full_label=case[0])
        assert double_label.organization == double_label.full_label.split(".")[0]
        assert double_label.role == double_label.full_label.split(".")[1]
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
        with pytest.raises(ValueError):
            TripleLabel(full_label=case[0])
    else:
        triple_label = TripleLabel(full_label=case[0])
        assert triple_label.metalabel == triple_label.full_label.split(".")[1]
        assert triple_label.label == triple_label.full_label.split(".")[2]
        assert triple_label.organization == triple_label.full_label.split(".")[0]
        assert triple_label.full_label == case[0]
