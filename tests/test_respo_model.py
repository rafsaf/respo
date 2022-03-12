import os
from typing import Tuple

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from respo import RoleLabel, TripleLabel
from respo.cli import app
from respo.core import AttributesContainer
from tests.conftest import get_model

valid_files = [file for file in os.scandir("./tests/cases/valid")]


@pytest.mark.parametrize("file", valid_files)
def test_respo_model_for_valid_cases(file: os.DirEntry, runner: CliRunner):
    get_model(file.path)
    result = runner.invoke(app, ["create", file.path])
    assert "Success!" in result.stdout


invalid_files = [file for file in os.scandir("./tests/cases/invalid")]


@pytest.mark.parametrize("file", invalid_files)
def test_respo_model_for_invalid_cases(file: os.DirEntry, runner: CliRunner):
    with pytest.raises(ValidationError):
        get_model(file.path)
    try:
        get_model(file.path)
    except ValidationError as exc:
        assert exc.errors()[0]["type"] in [
            "value_error.str.regex",
            "value_error.const",
            "value_error.respomodel",
        ]

    result = runner.invoke(app, ["create", file.path])
    assert "Could not validate respo model" in result.stdout


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


def test_attributes_container():
    item = AttributesContainer()

    with pytest.raises(ValueError):
        item.add_item("lowercase", "value")

    with pytest.raises(ValueError):
        item.add_item("SOME_NAME", set())  # type: ignore

    with pytest.raises(ValueError):
        item == "some string"
