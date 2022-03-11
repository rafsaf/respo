import pytest

from respo import BaseRespoModel, RespoClient, RespoError
from respo.respo_model import Organization


def test_create_respo_client_json_string_none():
    client = RespoClient(json_string=None)
    assert client._json_string == ""
    assert client.dict() == {"organizations": [], "roles": []}
    assert client.roles() == []
    assert client.organizations() == []
    assert str(client) == '{"organizations":[],"roles":[]}'


def test_create_respo_client_json_string_empty_string():
    client = RespoClient(json_string="")
    assert client._json_string == ""
    assert client.dict() == {"organizations": [], "roles": []}
    assert client.roles() == []
    assert client.organizations() == []
    assert str(client) == '{"organizations":[],"roles":[]}'


def test_create_respo_client_json_string_valid_not_trivial_json():
    client = RespoClient(
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
        RespoClient(json_string="sadcx")


def test_respo_client_add_and_remove_role(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()

    with pytest.raises(RespoError):
        assert client.add_role(
            "book123.not_exists", respo_model=None, validate_input=False
        )
    assert client.add_organization("book123", respo_model=respo, validate_input=False)
    assert client.add_role("book123.not_exists", respo_model=None, validate_input=False)
    assert client.roles() == ["book123.not_exists"]
    assert not client.add_role(
        "book123.not_exists", respo_model=respo, validate_input=False
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
        client.remove_role("book123.ERROR", respo_model=respo, validate_input=False)

    assert client.add_role("book123.not_exists", respo_model=None, validate_input=False)
    with pytest.raises(RespoError):
        client.add_role("book123.not_exists", respo_model=respo, validate_input=True)
    with pytest.raises(RespoError):
        client.add_role("book123.not_exists", respo_model=None, validate_input=True)
    with pytest.raises(RespoError):
        client.remove_role("book123.not_exists", respo_model=respo, validate_input=True)
    with pytest.raises(RespoError):
        client.remove_role("book123.not_exists", respo_model=None, validate_input=True)
    assert client.roles() == ["book123.not_exists"]
    assert client.remove_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )

    with pytest.raises(ValueError):
        client.add_role("not_exists", respo_model=None, validate_input=True)
    with pytest.raises(ValueError):
        client.remove_role("not_exists", respo_model=respo, validate_input=True)

    assert client.add_organization("default", validate_input=False)

    assert client.add_role(
        respo.ROLES.DEFAULT__SUPERUSER,  # type: ignore
        respo_model=respo,
        validate_input=True,
    )
    assert client.remove_role(
        respo.ROLES.DEFAULT__SUPERUSER,  # type: ignore
        respo_model=respo,
        validate_input=True,
    )


def test_respo_client_add_and_remove_organization(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    book_org: Organization = None  # type: ignore
    for role in respo.organizations:
        if role.metadata.label == "book123":
            book_org = role

    assert client.add_organization("book1234", respo_model=None, validate_input=False)
    assert not client.add_organization(
        "book1234", respo_model=respo, validate_input=False
    )
    assert client.organizations() == ["book1234"]
    assert client.remove_organization(
        "book1234", validate_input=False, respo_model=respo
    )
    assert client.organizations() == []
    assert not client.remove_organization(
        "book1234", validate_input=False, respo_model=None
    )

    with pytest.raises(RespoError):
        client.add_organization("book1234", respo_model=None, validate_input=True)
    with pytest.raises(RespoError):
        client.add_organization("book1234", respo_model=respo, validate_input=True)
    with pytest.raises(RespoError):
        client.remove_organization("book1234", respo_model=respo, validate_input=True)
    with pytest.raises(RespoError):
        client.remove_organization("book1234", respo_model=None, validate_input=True)

    assert client.add_organization(book_org, respo_model=respo, validate_input=True)
    assert client.remove_organization(book_org, respo_model=respo, validate_input=True)
    assert client.organizations() == []


def test_general_yml_organization_book123(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("book123", respo, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo)
    assert not client.has_permission("book123.user.all", respo)
    assert not client.has_permission("book123.user.read_all", respo)
    assert not client.has_permission("book123.user.read_all_better", respo)
    assert not client.has_permission("book123.user.delete", respo)

    assert client.has_permission("book123.book.list", respo)
    assert client.has_permission("book123.book.read", respo)
    assert client.has_permission("book123.book.buy_all", respo)
    assert client.has_permission("book123.book.buy", respo)
    assert not client.has_permission("book123.book.sell", respo)

    assert not client.has_permission("default.user.read_basic", respo)
    assert not client.has_permission("default.user.all", respo)
    assert not client.has_permission("default.user.read_all", respo)
    assert not client.has_permission("default.user.read_all_better", respo)
    assert not client.has_permission("default.user.update", respo)
    assert not client.has_permission("default.user.delete", respo)

    assert not client.has_permission("default.book.list", respo)
    assert not client.has_permission("default.book.read", respo)
    assert not client.has_permission("default.book.buy_all", respo)
    assert not client.has_permission("default.book.buy", respo)
    assert not client.has_permission("default.book.sell", respo)


def test_general_yml_organization_default(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("default", respo, validate_input=True)

    assert not client.has_permission("book123.user.read_basic", respo)
    assert not client.has_permission("book123.user.all", respo)
    assert not client.has_permission("book123.user.read_all", respo)
    assert not client.has_permission("book123.user.read_all_better", respo)
    assert not client.has_permission("book123.user.update", respo)
    assert not client.has_permission("book123.user.delete", respo)

    assert not client.has_permission("book123.book.list", respo)
    assert not client.has_permission("book123.book.read", respo)
    assert not client.has_permission("book123.book.buy_all", respo)
    assert not client.has_permission("book123.book.buy", respo)
    assert not client.has_permission("book123.book.sell", respo)

    assert client.has_permission("default.user.read_basic", respo)
    assert not client.has_permission("default.user.all", respo)
    assert client.has_permission("default.user.read_all", respo)
    assert client.has_permission("default.user.read_all_better", respo)
    assert not client.has_permission("default.user.update", respo)
    assert not client.has_permission("default.user.delete", respo)

    assert not client.has_permission("default.book.list", respo)
    assert not client.has_permission("default.book.read", respo)
    assert not client.has_permission("default.book.buy_all", respo)
    assert not client.has_permission("default.book.buy", respo)
    assert not client.has_permission("default.book.sell", respo)


def test_general_yml_role_client(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("default", respo, validate_input=True)
    assert client.add_organization("book123", respo, validate_input=True)
    assert client.add_role("book123.client", respo, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo)
    assert not client.has_permission("book123.user.all", respo)
    assert not client.has_permission("book123.user.read_all", respo)
    assert not client.has_permission("book123.user.read_all_better", respo)
    assert not client.has_permission("book123.user.update", respo)
    assert not client.has_permission("book123.user.delete", respo)

    assert client.has_permission("book123.book.list", respo)
    assert client.has_permission("book123.book.read", respo)
    assert client.has_permission("book123.book.buy_all", respo)
    assert client.has_permission("book123.book.buy", respo)
    assert not client.has_permission("book123.book.sell", respo)

    assert client.has_permission("default.user.read_basic", respo)
    assert not client.has_permission("default.user.all", respo)
    assert client.has_permission("default.user.read_all", respo)
    assert client.has_permission("default.user.read_all_better", respo)
    assert not client.has_permission("default.user.update", respo)
    assert not client.has_permission("default.user.delete", respo)

    assert not client.has_permission("default.book.list", respo)
    assert not client.has_permission("default.book.read", respo)
    assert not client.has_permission("default.book.buy_all", respo)
    assert not client.has_permission("default.book.buy", respo)
    assert not client.has_permission("default.book.sell", respo)


def test_general_yml_role_superuser_book(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("default", respo, validate_input=True)
    assert client.add_organization("book123", respo, validate_input=True)
    assert client.add_role("book123.superuser_book", respo, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo)
    assert client.has_permission("book123.user.all", respo)
    assert client.has_permission("book123.user.read_all", respo)
    assert client.has_permission("book123.user.read_all_better", respo)
    assert client.has_permission("book123.user.update", respo)
    assert client.has_permission("book123.user.delete", respo)

    assert client.has_permission("book123.book.list", respo)
    assert client.has_permission("book123.book.read", respo)
    assert client.has_permission("book123.book.buy_all", respo)
    assert client.has_permission("book123.book.buy", respo)
    assert not client.has_permission("book123.book.sell", respo)

    assert client.has_permission("default.user.read_basic", respo)
    assert not client.has_permission("default.user.all", respo)
    assert client.has_permission("default.user.read_all", respo)
    assert client.has_permission("default.user.read_all_better", respo)
    assert not client.has_permission("default.user.update", respo)
    assert not client.has_permission("default.user.delete", respo)

    assert not client.has_permission("default.book.list", respo)
    assert not client.has_permission("default.book.read", respo)
    assert not client.has_permission("default.book.buy_all", respo)
    assert not client.has_permission("default.book.buy", respo)
    assert not client.has_permission("default.book.sell", respo)


def test_general_yml_role_admin_role(get_general_model: BaseRespoModel):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("default", respo, validate_input=True)
    assert client.add_organization("book123", respo, validate_input=True)
    assert client.add_role("book123.admin_role", respo, validate_input=True)

    assert client.has_permission("book123.user.read_basic", respo)
    assert not client.has_permission("book123.user.all", respo)
    assert client.has_permission("book123.user.read_all", respo)
    assert not client.has_permission("book123.user.read_all_better", respo)
    assert not client.has_permission("book123.user.update", respo)
    assert not client.has_permission("book123.user.delete", respo)

    assert client.has_permission("book123.book.list", respo)
    assert client.has_permission("book123.book.read", respo)
    assert client.has_permission("book123.book.buy_all", respo)
    assert client.has_permission("book123.book.buy", respo)
    assert client.has_permission("book123.book.sell", respo)

    assert client.has_permission("default.user.read_basic", respo)
    assert not client.has_permission("default.user.all", respo)
    assert client.has_permission("default.user.read_all", respo)
    assert client.has_permission("default.user.read_all_better", respo)
    assert not client.has_permission("default.user.update", respo)
    assert not client.has_permission("default.user.delete", respo)

    assert not client.has_permission("default.book.list", respo)
    assert not client.has_permission("default.book.read", respo)
    assert not client.has_permission("default.book.buy_all", respo)
    assert not client.has_permission("default.book.buy", respo)
    assert not client.has_permission("default.book.sell", respo)
