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


role_label_cases = [
    ("foobar.read", False),
    ("barread ", False),
    (" barread", False),
    ("bar#$read@", False),
    ("bar44ź3read", False),
    ("bar read", False),
    ("bar. read", False),
    ("barread.x", False),
    ("barread.", False),
    (".barread", False),
    ("barread", True),
    ("bar2_read_5", True),
]


@pytest.mark.parametrize("case", role_label_cases)
def test_role_label(case: Tuple[str, bool]):
    if case[1] is False:
        with pytest.raises(ValueError):
            respo.RoleLabel(role_name=case[0])
    else:
        role_label = respo.RoleLabel(role_name=case[0])
        assert role_label.role_label == case[0]
        assert str(role_label) == case[0]


permission_label_cases = [
    ("bar_read", False),
    ("foo.bar.read ", False),
    (" bar.read", False),
    ("foo.bar ", False),
    ("foXo.bar ", False),
    ("fożźo.bar ", False),
    ("foo.b^&r ", False),
    ("foo.bar.", False),
    ("foo.bar.read.x", False),
    ("foo .bar", False),
    ("foo.foo2X", False),
    ("foo.bar", True),
    ("foo1.bar2", True),
]


@pytest.mark.parametrize("case", permission_label_cases)
def test_permission_label(case: Tuple[str, bool]):
    if case[1] is False:
        with pytest.raises(ValueError):
            respo.PermissionLabel(permission_name=case[0])
    else:
        permission_label = respo.PermissionLabel(permission_name=case[0])
        assert permission_label.collection == case[0].split(".")[0]
        assert permission_label.label == case[0].split(".")[1]
        assert permission_label.permission_name == case[0]
        assert str(permission_label) == case[0]


def test_model_perms(get_general_model: respo.RespoModel):
    assert get_general_model.PERMS.respo_model == get_general_model
    for perm in get_general_model.PERMS:
        assert perm in get_general_model.permissions
        assert perm in get_general_model.PERMS
    assert len(get_general_model.PERMS) == len(get_general_model.permissions)

    roles1 = respo.PERMSContainer(get_general_model)
    assert roles1 == get_general_model.PERMS

    with pytest.raises(ValueError):
        get_general_model.PERMS == ""


def test_model_roles(get_general_model: respo.RespoModel):
    assert get_general_model.ROLES.respo_model == get_general_model
    for role in get_general_model.ROLES:
        assert role in get_general_model.roles_permissions
        assert role in get_general_model.ROLES
        assert get_general_model.roles_permissions[
            role
        ] == get_general_model.ROLES.permissions(role)
    assert len(get_general_model.ROLES) == len(get_general_model.roles_permissions)

    perms1 = respo.ROLESContainer(get_general_model)
    assert perms1 == get_general_model.ROLES

    with pytest.raises(ValueError):
        get_general_model.ROLES == ""

    with pytest.raises(ValueError):
        get_general_model.ROLES.permissions("xxx")
