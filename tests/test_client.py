from typing import Tuple
from respo.client import create_respo_client, Client
import pytest

cases = [
    (None, []),
    ("xxxxxx", ["xxxxxx"]),
    (["xxxxxx"], ["xxxxxx"]),
    ("x1 x2 x3", ["x1", "x2", "x3"]),
    (["x1", "x2", "x3"], ["x1", "x2", "x3"]),
]


@pytest.mark.parametrize("case", cases)
def test_create_respo_client_ok_for_every_input(case: Tuple[str, str]):
    client = create_respo_client(role=case[0], organization=case[0])
    assert client.organization == case[1]
    assert client.role == case[1]