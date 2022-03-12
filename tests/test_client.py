import pytest

import respo


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


def test_respo_client_add_and_remove_role(get_general_model: respo.RespoModel):
    respo_model = get_general_model
    client = respo.RespoClient()

    assert client.add_role("book123.not_exists", respo_model=None, validate_input=False)
    assert not client.add_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )
    assert client.roles() == ["book123.not_exists"]
    assert client.organizations() == ["book123"]
    assert not client.add_role(
        "book123.not_exists", respo_model=respo_model, validate_input=False
    )
    assert client.roles() == ["book123.not_exists"]
    assert client.remove_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )
    assert not client.remove_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )
    assert client.roles() == []

    with pytest.raises(ValueError):
        client.add_role("book123.ERROR", respo_model=None, validate_input=False)
    with pytest.raises(ValueError):
        client.remove_role(
            "book123.ERROR", respo_model=respo_model, validate_input=False
        )

    assert client.add_role("book123.not_exists", respo_model=None, validate_input=False)
    with pytest.raises(respo.RespoClientError):
        client.add_role(
            "book123.not_exists", respo_model=respo_model, validate_input=True
        )
    with pytest.raises(TypeError):
        client.add_role("book123.not_exists", respo_model=None, validate_input=True)
    with pytest.raises(respo.RespoClientError):
        client.remove_role(
            "book123.not_exists", respo_model=respo_model, validate_input=True
        )
    assert client.roles() == ["book123.not_exists"]
    assert client.remove_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )

    with pytest.raises(TypeError):
        client.add_role("not_exists", respo_model=None, validate_input=True)
    with pytest.raises(ValueError):
        client.remove_role("not_exists", respo_model=respo_model, validate_input=True)

    assert client.add_role(
        respo_model.ROLES.DEFAULT__SUPERUSER,  # type: ignore
        respo_model=respo_model,
        validate_input=True,
    )
    assert client.remove_role(
        respo_model.ROLES.DEFAULT__SUPERUSER,  # type: ignore
        respo_model=respo_model,
        validate_input=True,
    )


def test_respo_client_add_and_remove_organization(get_general_model: respo.RespoModel):
    respo_model = get_general_model
    client = respo.RespoClient()

    assert client.add_organization("book1234", respo_model=None, validate_input=False)
    assert not client.add_organization(
        "book1234", respo_model=respo_model, validate_input=False
    )
    assert client.organizations() == ["book1234"]
    assert client.remove_organization(
        "book1234", validate_input=False, respo_model=respo_model
    )
    assert client.organizations() == []
    assert not client.remove_organization(
        "book1234", validate_input=False, respo_model=None
    )

    with pytest.raises(TypeError):
        client.add_organization("book1234", respo_model=None, validate_input=True)
    with pytest.raises(respo.RespoClientError):
        client.add_organization(
            "book1234", respo_model=respo_model, validate_input=True
        )

    assert client.add_organization(
        respo_model.ORGS.BOOK123, respo_model=respo_model, validate_input=True  # type: ignore
    )
    assert client.remove_organization(
        respo_model.ORGS.BOOK123, respo_model=respo_model, validate_input=True  # type: ignore
    )
    assert client.organizations() == []


def test_general_yml_organization_book123(get_general_model: respo.RespoModel):
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


def test_general_yml_organization_default(get_general_model: respo.RespoModel):
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


def test_general_yml_role_client(get_general_model: respo.RespoModel):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_organization("book123", respo_model, validate_input=True)
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


def test_general_yml_role_superuser_book(get_general_model: respo.RespoModel):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_organization("book123", respo_model, validate_input=True)
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


def test_general_yml_role_admin_role(get_general_model: respo.RespoModel):
    respo_model = get_general_model
    client = respo.RespoClient()
    assert client.add_organization("default", respo_model, validate_input=True)
    assert client.add_organization("book123", respo_model, validate_input=True)
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
