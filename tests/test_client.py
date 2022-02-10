from typing import Tuple

import pytest

from respo import RespoClient

cases = [
    (None, []),
    (["xxxxxx"], ["xxxxxx"]),
    ("x1 x2 x3", ["x1", "x2", "x3"]),
    (["x1", "x2", "x3"], ["x1", "x2", "x3"]),
]


@pytest.mark.parametrize("case", cases)
def test_create_respo_client_ok_for_every_input(case: Tuple[str, str]):
    client = RespoClient()
    pass
