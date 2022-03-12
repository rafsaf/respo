from typing import Optional, Union

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


@pytest.fixture(scope="function")
def get_org_label(request, get_general_model: respo.RespoModel):
    if request.param.isupper():
        return getattr(get_general_model.ORGS, request.param)
    else:
        return request.param


def test_create_respo_client_json_string_none():
    client = respo.RespoClient(json_string=None)
    assert client._json_string == ""
    assert client.dict() == {"organizations": [], "roles": []}
    assert client.roles() == []
    assert client.organizations() == []
    assert str(client) == '{"organizations":[],"roles":[]}'


def test_create_respo_client_json_string_empty_string():
    client = respo.RespoClient(json_string="")
    assert client._json_string == ""
    assert client.dict() == {"organizations": [], "roles": []}
    assert client.roles() == []
    assert client.organizations() == []
    assert str(client) == '{"organizations":[],"roles":[]}'


def test_create_respo_client_json_string_valid_not_trivial_json():
    client = respo.RespoClient(
        json_string='{"organizations":["test_org_x"],"roles":["test_org_x.test_role_y"]}'
    )
    assert (
        client._json_string
        == '{"organizations":["test_org_x"],"roles":["test_org_x.test_role_y"]}'
    )
    assert client.dict() == {
        "organizations": ["test_org_x"],
        "roles": ["test_org_x.test_role_y"],
    }
    assert client.roles() == ["test_org_x.test_role_y"]
    assert client.organizations() == ["test_org_x"]
    assert (
        str(client)
        == '{"organizations":["test_org_x"],"roles":["test_org_x.test_role_y"]}'
    )


def test_create_respo_client_json_string_no_sense():
    with pytest.raises(ValueError):
        respo.RespoClient(json_string="sadcx")


add_remove_role_exc_cases = [
    ("book123.UpPeR", None, False, ValueError),
    ("śćżźć.not_ascii", None, False, ValueError),
    ("symbols&^@", None, False, ValueError),
    ("single_label", None, False, ValueError),
    ("and.triple.label", None, False, ValueError),
    ("valid.label", None, True, TypeError),
    ("valid.label", "general_model", True, respo.RespoClientError),
    ("book123.not_exists", "general_model", True, respo.RespoClientError),
    ("DEFAULT__SUPERUSER", None, True, TypeError),
]


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input, exc_class",
    add_remove_role_exc_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_respo_client_add_role_raise_errors_when_invalid_data(
    get_role_label: Union[str, respo.Role],
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
    get_role_label: Union[str, respo.Role],
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
    ("valid.label", None, False),
    ("valid_123.label_433", None, False),
    ("DEFAULT__SUPERUSER", None, False),
    ("BOOK123__ROOT", None, False),
    ("BOOK123__ROOT", "general_model", True),
    ("default.superuser", "general_model", True),
]


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input",
    add_remove_role_success_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_add_role_properly_created(
    get_role_label: Union[str, respo.Role],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_role(get_role_label, get_respo_model, validate_input)
    assert not respo_client.add_role(get_role_label, get_respo_model, validate_input)

    role_label = str(get_role_label)
    assert role_label in respo_client.roles()
    org_for_role = role_label.split(".")[0]
    assert org_for_role in respo_client.organizations()


@pytest.mark.parametrize(
    "get_role_label, get_respo_model, validate_input",
    add_remove_role_success_cases,
    indirect=["get_role_label", "get_respo_model"],
)
def test_remove_role_properly_removed(
    get_role_label: Union[str, respo.Role],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_role(get_role_label, get_respo_model, validate_input)
    assert respo_client.remove_role(get_role_label, get_respo_model, validate_input)
    assert not respo_client.remove_role(get_role_label, get_respo_model, validate_input)

    assert respo_client.organizations()
    assert not respo_client.roles()


add_remove_organization_exc_cases = [
    ("UpPeR", None, False, ValueError),
    ("śćżźć_not_ascii", None, False, ValueError),
    ("symbols&^@", None, False, ValueError),
    ("double.label", None, False, ValueError),
    ("and.triple.label", None, False, ValueError),
    ("valid", None, True, TypeError),
    ("not_exist", "general_model", True, respo.RespoClientError),
    ("DEFAULT", None, True, TypeError),
]


@pytest.mark.parametrize(
    "get_org_label, get_respo_model, validate_input, exc_class",
    add_remove_organization_exc_cases,
    indirect=["get_org_label", "get_respo_model"],
)
def test_respo_client_add_organization_raise_errors_when_invalid_data(
    get_org_label: Union[str, respo.Organization],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
    exc_class,
):
    respo_client = respo.RespoClient()
    with pytest.raises(exc_class):
        respo_client.add_organization(
            organization_name=get_org_label,
            respo_model=get_respo_model,
            validate_input=validate_input,
        )


@pytest.mark.parametrize(
    "get_org_label, get_respo_model, validate_input, exc_class",
    add_remove_organization_exc_cases,
    indirect=["get_org_label", "get_respo_model"],
)
def test_respo_client_remove_organization_raise_errors_when_invalid_data(
    get_org_label: Union[str, respo.Organization],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
    exc_class,
):
    respo_client = respo.RespoClient()
    with pytest.raises(exc_class):
        respo_client.remove_organization(
            organization_name=get_org_label,
            respo_model=get_respo_model,
            validate_input=validate_input,
        )


add_remove_organization_success_cases = [
    ("valid", None, False),
    ("valid_123", None, False),
    ("DEFAULT", None, False),
    ("BOOK123", None, False),
    ("BOOK123", "general_model", True),
    ("default", "general_model", True),
]


@pytest.mark.parametrize(
    "get_org_label, get_respo_model, validate_input",
    add_remove_organization_success_cases,
    indirect=["get_org_label", "get_respo_model"],
)
def test_respo_client_add_organization_properly_added(
    get_org_label: Union[str, respo.Organization],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_organization(
        organization_name=get_org_label,
        respo_model=get_respo_model,
        validate_input=validate_input,
    )
    assert not respo_client.add_organization(
        organization_name=get_org_label,
        respo_model=get_respo_model,
        validate_input=validate_input,
    )
    assert respo_client.organizations() == [str(get_org_label)]


@pytest.mark.parametrize(
    "get_org_label, get_respo_model, validate_input",
    add_remove_organization_success_cases,
    indirect=["get_org_label", "get_respo_model"],
)
def test_respo_client_remove_organization_properly_removed(
    get_org_label: Union[str, respo.Organization],
    get_respo_model: Optional[respo.RespoModel],
    validate_input: bool,
):
    respo_client = respo.RespoClient()
    assert respo_client.add_organization(
        organization_name=get_org_label,
        respo_model=get_respo_model,
        validate_input=validate_input,
    )
    assert respo_client.add_role(f"{str(get_org_label)}.test1", validate_input=False)
    assert respo_client.remove_organization(
        organization_name=get_org_label,
        respo_model=get_respo_model,
        validate_input=validate_input,
    )
    assert not respo_client.remove_organization(
        organization_name=get_org_label,
        respo_model=get_respo_model,
        validate_input=validate_input,
    )
    assert not respo_client.organizations()
    assert not respo_client.roles()


def test_client_has_permission_organization_book123(
    get_general_model: respo.RespoModel,
):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("book123", respo_model, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo_model)
    assert not client.has_permission("book123.user.all", respo_model)
    assert not client.has_permission("book123.user.read_all", respo_model)
    assert not client.has_permission("book123.user.read_all_better", respo_model)
    assert not client.has_permission("book123.user.delete", respo_model)

    assert client.has_permission("book123.book.list", respo_model)
    assert client.has_permission("book123.book.read", respo_model)
    assert client.has_permission("book123.book.buy_all", respo_model)
    assert client.has_permission("book123.book.buy", respo_model)
    assert not client.has_permission("book123.book.sell", respo_model)

    assert not client.has_permission("default.user.read_basic", respo_model)
    assert not client.has_permission("default.user.all", respo_model)
    assert not client.has_permission("default.user.read_all", respo_model)
    assert not client.has_permission("default.user.read_all_better", respo_model)
    assert not client.has_permission("default.user.update", respo_model)
    assert not client.has_permission("default.user.delete", respo_model)

    assert not client.has_permission("default.book.list", respo_model)
    assert not client.has_permission("default.book.read", respo_model)
    assert not client.has_permission("default.book.buy_all", respo_model)
    assert not client.has_permission("default.book.buy", respo_model)
    assert not client.has_permission("default.book.sell", respo_model)


def test_client_has_permission_organization_default(
    get_general_model: respo.RespoModel,
):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)

    assert not client.has_permission("book123.user.read_basic", respo_model)
    assert not client.has_permission("book123.user.all", respo_model)
    assert not client.has_permission("book123.user.read_all", respo_model)
    assert not client.has_permission("book123.user.read_all_better", respo_model)
    assert not client.has_permission("book123.user.update", respo_model)
    assert not client.has_permission("book123.user.delete", respo_model)

    assert not client.has_permission("book123.book.list", respo_model)
    assert not client.has_permission("book123.book.read", respo_model)
    assert not client.has_permission("book123.book.buy_all", respo_model)
    assert not client.has_permission("book123.book.buy", respo_model)
    assert not client.has_permission("book123.book.sell", respo_model)

    assert client.has_permission("default.user.read_basic", respo_model)
    assert not client.has_permission("default.user.all", respo_model)
    assert client.has_permission("default.user.read_all", respo_model)
    assert client.has_permission("default.user.read_all_better", respo_model)
    assert not client.has_permission("default.user.update", respo_model)
    assert not client.has_permission("default.user.delete", respo_model)

    assert not client.has_permission("default.book.list", respo_model)
    assert not client.has_permission("default.book.read", respo_model)
    assert not client.has_permission("default.book.buy_all", respo_model)
    assert not client.has_permission("default.book.buy", respo_model)
    assert not client.has_permission("default.book.sell", respo_model)


def test_client_has_permission_role_client_organization_default(
    get_general_model: respo.RespoModel,
):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_role("book123.client", respo_model, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo_model)
    assert not client.has_permission("book123.user.all", respo_model)
    assert not client.has_permission("book123.user.read_all", respo_model)
    assert not client.has_permission("book123.user.read_all_better", respo_model)
    assert not client.has_permission("book123.user.update", respo_model)
    assert not client.has_permission("book123.user.delete", respo_model)

    assert client.has_permission("book123.book.list", respo_model)
    assert client.has_permission("book123.book.read", respo_model)
    assert client.has_permission("book123.book.buy_all", respo_model)
    assert client.has_permission("book123.book.buy", respo_model)
    assert not client.has_permission("book123.book.sell", respo_model)

    assert client.has_permission("default.user.read_basic", respo_model)
    assert not client.has_permission("default.user.all", respo_model)
    assert client.has_permission("default.user.read_all", respo_model)
    assert client.has_permission("default.user.read_all_better", respo_model)
    assert not client.has_permission("default.user.update", respo_model)
    assert not client.has_permission("default.user.delete", respo_model)

    assert not client.has_permission("default.book.list", respo_model)
    assert not client.has_permission("default.book.read", respo_model)
    assert not client.has_permission("default.book.buy_all", respo_model)
    assert not client.has_permission("default.book.buy", respo_model)
    assert not client.has_permission("default.book.sell", respo_model)


def test_client_has_permission_role_superuser_book123_organization_default(
    get_general_model: respo.RespoModel,
):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_role("book123.superuser_book", respo_model, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo_model)
    assert client.has_permission("book123.user.all", respo_model)
    assert client.has_permission("book123.user.read_all", respo_model)
    assert client.has_permission("book123.user.read_all_better", respo_model)
    assert client.has_permission("book123.user.update", respo_model)
    assert client.has_permission("book123.user.delete", respo_model)

    assert client.has_permission("book123.book.list", respo_model)
    assert client.has_permission("book123.book.read", respo_model)
    assert client.has_permission("book123.book.buy_all", respo_model)
    assert client.has_permission("book123.book.buy", respo_model)
    assert not client.has_permission("book123.book.sell", respo_model)

    assert client.has_permission("default.user.read_basic", respo_model)
    assert not client.has_permission("default.user.all", respo_model)
    assert client.has_permission("default.user.read_all", respo_model)
    assert client.has_permission("default.user.read_all_better", respo_model)
    assert not client.has_permission("default.user.update", respo_model)
    assert not client.has_permission("default.user.delete", respo_model)

    assert not client.has_permission("default.book.list", respo_model)
    assert not client.has_permission("default.book.read", respo_model)
    assert not client.has_permission("default.book.buy_all", respo_model)
    assert not client.has_permission("default.book.buy", respo_model)
    assert not client.has_permission("default.book.sell", respo_model)


def test_client_has_permission_role_admin_role_organization_default(
    get_general_model: respo.RespoModel,
):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_role("book123.admin_role", respo_model, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo_model)
    assert not client.has_permission("book123.user.all", respo_model)
    assert client.has_permission("book123.user.read_all", respo_model)
    assert not client.has_permission("book123.user.read_all_better", respo_model)
    assert not client.has_permission("book123.user.update", respo_model)
    assert not client.has_permission("book123.user.delete", respo_model)

    assert client.has_permission("book123.book.list", respo_model)
    assert client.has_permission("book123.book.read", respo_model)
    assert client.has_permission("book123.book.buy_all", respo_model)
    assert client.has_permission("book123.book.buy", respo_model)
    assert client.has_permission("book123.book.sell", respo_model)

    assert client.has_permission("default.user.read_basic", respo_model)
    assert not client.has_permission("default.user.all", respo_model)
    assert client.has_permission("default.user.read_all", respo_model)
    assert client.has_permission("default.user.read_all_better", respo_model)
    assert not client.has_permission("default.user.update", respo_model)
    assert not client.has_permission("default.user.delete", respo_model)

    assert not client.has_permission("default.book.list", respo_model)
    assert not client.has_permission("default.book.read", respo_model)
    assert not client.has_permission("default.book.buy_all", respo_model)
    assert not client.has_permission("default.book.buy", respo_model)
    assert not client.has_permission("default.book.sell", respo_model)
