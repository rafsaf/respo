import pytest
from pydantic import ValidationError

from respo import BaseRespoModel, RespoClient, RespoException
from respo.respo_model import Organization, Role


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
    book_role: Role = None  # type: ignore
    for role in respo.roles:
        if role.metadata.label == "client" and role.metadata.organization == "book123":
            book_role = role
    with pytest.raises(RespoException):
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

    with pytest.raises(ValidationError):
        client.add_role("book123.ERROR", respo_model=None, validate_input=False)
    with pytest.raises(ValidationError):
        client.remove_role("book123.ERROR", respo_model=respo, validate_input=False)

    assert client.add_role("book123.not_exists", respo_model=None, validate_input=False)
    with pytest.raises(RespoException):
        client.add_role("book123.not_exists", respo_model=respo, validate_input=True)
    with pytest.raises(RespoException):
        client.add_role("book123.not_exists", respo_model=None, validate_input=True)
    with pytest.raises(RespoException):
        client.remove_role("book123.not_exists", respo_model=respo, validate_input=True)
    with pytest.raises(RespoException):
        client.remove_role("book123.not_exists", respo_model=None, validate_input=True)
    assert client.roles() == ["book123.not_exists"]
    assert client.remove_role(
        "book123.not_exists", respo_model=None, validate_input=False
    )

    with pytest.raises(ValidationError):
        client.add_role("not_exists", respo_model=None, validate_input=True)
    with pytest.raises(ValidationError):
        client.remove_role("not_exists", respo_model=respo, validate_input=True)

    assert client.add_role(book_role, respo_model=respo, validate_input=True)
    assert client.remove_role(book_role, respo_model=respo, validate_input=True)


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

    with pytest.raises(RespoException):
        client.add_organization("book1234", respo_model=None, validate_input=True)
    with pytest.raises(RespoException):
        client.add_organization("book1234", respo_model=respo, validate_input=True)
    with pytest.raises(RespoException):
        client.remove_organization("book1234", respo_model=respo, validate_input=True)
    with pytest.raises(RespoException):
        client.remove_organization("book1234", respo_model=None, validate_input=True)

    assert client.add_organization(book_org, respo_model=respo, validate_input=True)
    assert client.remove_organization(book_org, respo_model=respo, validate_input=True)
    assert client.organizations() == []
