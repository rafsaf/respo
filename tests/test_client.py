from typing import Optional

import pytest

import respo


@pytest.fixture(scope="function")
def get_respo_model(request, get_general_model: respo.RespoModel):
    if request.param == "general_model":
        return get_general_model
    else:
        return None


@pytest.fixture(scope="function")
def get_role_label(request, get_general_model: respo.RespoModel):
    if request.param.isupper():
        return getattr(get_general_model.ROLES, request.param)
    else:
        return request.param


def test_create_respo_client_init():
    client = respo.RespoClient(roles="")
    assert client.roles == []
    assert str(client) == ""

    client = respo.RespoClient(roles="")
    assert client.roles == []
    assert str(client) == ""

    client = respo.RespoClient(roles="xxx,yyy,123_123")
    assert client.roles == ["xxx", "yyy", "123_123"]
    assert str(client) == "xxx,yyy,123_123"


add_remove_role_exc_cases = [
    ("book123_UpPeR", None, False, ValueError),
    ("śćżźć_not_ascii", None, False, ValueError),
    ("symbols&^@", None, False, ValueError),
    ("double.label", None, False, ValueError),
    ("and.triple.label", None, False, ValueError),
    ("valid_label", None, True, TypeError),
    ("valid_label", "general_model", True, respo.RespoClientError),
    ("book123_not_exists", "general_model", True, respo.RespoClientError),
    ("DEFAULT", None, True, TypeError),
]


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input, exc_class",
    add_remove_role_exc_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_respo_client_add_role_raise_errors_when_invalid_data(
    get_role_label: str,
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
    exc_class,
):
    respo_client = respo.RespoClient()
    with pytest.raises(exc_class):
        respo_client.add_role(
            role_name=get_role_label,
            respo_model=get_respo_model,
            validate_input=validate_input,
        )


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input, exc_class",
    add_remove_role_exc_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_respo_client_remove_role_raise_errors_when_invalid_data(
    get_role_label: str,
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
    exc_class,
):
    respo_client = respo.RespoClient()
    with pytest.raises(exc_class):
        respo_client.remove_role(
            role_name=get_role_label,
            respo_model=get_respo_model,
            validate_input=validate_input,
        )


add_remove_role_success_cases = [
    ("valid_label", None, False),
    ("valid_123_label_433", None, False),
    ("DEFAULT", None, False),
    ("ADMIN", None, False),
    ("ADMIN", "general_model", True),
    ("default", "general_model", True),
    ("admin", "general_model", True),
]


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input",
    add_remove_role_success_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_add_role_properly_created(
    get_role_label: str,
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_role(get_role_label, get_respo_model, validate_input)
    assert not respo_client.add_role(get_role_label, get_respo_model, validate_input)

    role_label = str(get_role_label)
    assert role_label in respo_client.roles


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input",
    add_remove_role_success_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_remove_role_properly_removed(
    get_role_label: str,
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_role(get_role_label, get_respo_model, validate_input)
    assert respo_client.remove_role(get_role_label, get_respo_model, validate_input)
    assert not respo_client.remove_role(get_role_label, get_respo_model, validate_input)
    assert not respo_client.roles


def test_client_permissions_admin(get_general_model: respo.RespoModel):

    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_role("admin", respo_model, validate_input=True)

    assert client.has_permission("user.read_basic", respo_model)
    assert client.has_permission("user.read_all_better", respo_model)
    assert client.has_permission("user.read_all", respo_model)
    assert not client.has_permission("user.update", respo_model)

    assert client.has_permission("book.list", respo_model)
    assert client.has_permission("book.read", respo_model)
    assert not client.has_permission("book.sell", respo_model)
    assert not client.has_permission("book.buy", respo_model)


def test_client_permissions_default(get_general_model: respo.RespoModel):

    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_role("default", respo_model, validate_input=True)

    assert client.has_permission("user.read_basic", respo_model)
    assert not client.has_permission("user.read_all_better", respo_model)
    assert client.has_permission("user.read_all", respo_model)
    assert not client.has_permission("user.update", respo_model)

    assert client.has_permission("book.list", respo_model)
    assert client.has_permission("book.read", respo_model)
    assert not client.has_permission("book.sell", respo_model)
    assert not client.has_permission("book.buy", respo_model)


def test_client_permissions_pro_user(get_general_model: respo.RespoModel):

    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_role("pro_user", respo_model, validate_input=True)

    assert client.has_permission("user.read_basic", respo_model)
    assert not client.has_permission("user.read_all_better", respo_model)
    assert client.has_permission("user.read_all", respo_model)
    assert not client.has_permission("user.update", respo_model)

    assert client.has_permission("book.list", respo_model)
    assert client.has_permission("book.read", respo_model)
    assert client.has_permission("book.sell", respo_model)
    assert not client.has_permission("book.buy", respo_model)


def test_client_permissions_superadmin(get_general_model: respo.RespoModel):

    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_role("superadmin", respo_model, validate_input=True)

    assert client.has_permission("user.read_basic", respo_model)
    assert client.has_permission("user.read_all_better", respo_model)
    assert client.has_permission("user.read_all", respo_model)
    assert client.has_permission("user.update", respo_model)

    assert client.has_permission("book.list", respo_model)
    assert client.has_permission("book.read", respo_model)
    assert client.has_permission("book.sell", respo_model)
    assert not client.has_permission("book.buy", respo_model)
