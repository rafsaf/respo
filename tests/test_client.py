from typing import Tuple

import pytest

from respo.client import create_respo_client

cases = [
    (None, []),
    ("xxxxxx", ["xxxxxx"]),
    (["xxxxxx"], ["xxxxxx"]),
    ("x1 x2 x3", ["x1", "x2", "x3"]),
    (["x1", "x2", "x3"], ["x1", "x2", "x3"]),
]


@pytest.mark.parametrize("case", cases)
def test_create_respo_client_ok_for_every_input(case: Tuple[str, str]):
    client = create_respo_client(roles=case[0], organizations=case[0])
    assert client.organizations == case[1]
    assert client.roles == case[1]
