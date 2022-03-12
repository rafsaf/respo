import os
from typing import Tuple

import pydantic
import pytest
from click import testing

import respo
from respo import cli
from tests import conftest


def test_respo_model_get_respo_model_throw_errors():
    respo.config.RESPO_AUTO_FOLDER_NAME = "/12309-8)A(S*D)_A(S*D)_(A*DS/asdasdasd"
    with pytest.raises(respo.RespoModelError):
        respo.RespoModel.get_respo_model(yml_file=False)
    with pytest.raises(respo.RespoModelError):
        respo.RespoModel.get_respo_model(yml_file=True)


valid_files = [file for file in os.scandir("./tests/cases/valid")]


@pytest.mark.parametrize("file", valid_files)
def test_respo_model_for_valid_cases(file: os.DirEntry, runner: testing.CliRunner):
    conftest.get_model(file.path)
    result = runner.invoke(cli.app, ["create", file.path])
    assert "Success!" in result.stdout


invalid_files = [file for file in os.scandir("./tests/cases/invalid")]


@pytest.mark.parametrize("file", invalid_files)
def test_respo_model_for_invalid_cases(file: os.DirEntry, runner: testing.CliRunner):
    with pytest.raises(pydantic.ValidationError):
        conftest.get_model(file.path)
    try:
        conftest.get_model(file.path)
    except pydantic.ValidationError as exc:
        assert exc.errors()[0]["type"] in [
            "value_error.str.regex",
            "value_error.const",
            "value_error.respomodel",
        ]

    result = runner.invoke(cli.app, ["create", file.path])
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
            respo.RoleLabel(full_label=case[0])
    else:
        double_label = respo.RoleLabel(full_label=case[0])
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
            respo.PermissionLabel(full_label=case[0])
    else:
        triple_label = respo.PermissionLabel(full_label=case[0])
        assert triple_label.metalabel == triple_label.full_label.split(".")[1]
        assert triple_label.label == triple_label.full_label.split(".")[2]
        assert triple_label.organization == triple_label.full_label.split(".")[0]
        assert triple_label.full_label == case[0]


def test_attributes_container():
    item = respo.AttributesContainer()

    with pytest.raises(ValueError):
        item._add_item("lowercase", "value")

    with pytest.raises(ValueError):
        item._add_item("SOME_NAME", set())  # type: ignore

    with pytest.raises(ValueError):
        item == "some string"


def test_organization_label(get_general_model: respo.RespoModel):
    organization_label1 = respo.OrganizationLabel("org")
    assert organization_label1.organization == "org"
    assert str(organization_label1) == "org"
    organization_label2 = respo.OrganizationLabel(get_general_model.ORGS.DEFAULT)  # type: ignore
    assert organization_label2.organization == "default"
    assert str(organization_label2) == "default"


def test_role_label(get_general_model: respo.RespoModel):
    role_label1 = respo.RoleLabel("org.role")
    assert role_label1.organization == "org"
    assert role_label1.full_label == "org.role"
    assert role_label1.role == "role"
    assert str(role_label1) == "org.role"
    role_label2 = respo.RoleLabel(get_general_model.ROLES.DEFAULT__ROOT)  # type: ignore
    assert role_label2.organization == "default"
    assert role_label2.full_label == "default.root"
    assert role_label2.role == "root"
    assert str(role_label2) == "default.root"
