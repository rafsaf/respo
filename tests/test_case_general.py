from pydantic import ValidationError
import pytest

from respo import BaseRespoModel, RespoClient, RespoException


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


def test_general_yml_not_existing_role_validation_raise_error(
    get_general_model: BaseRespoModel,
):
    respo = get_general_model
    client = RespoClient()
    assert client.add_organization("test_org_x", validate_input=False)
    with pytest.raises(RespoException):
        client.add_role("test_org_x.test_role_y", respo, validate_input=True)


def test_general_yml_invalid_syntax_no_dot_error(
    get_general_model: BaseRespoModel,
):
    respo = get_general_model
    client = RespoClient()
    with pytest.raises(ValidationError):
        client.add_role("test_role_y", respo, validate_input=True)
    with pytest.raises(ValidationError):
        client.add_role("test_role_y", validate_input=False)


def test_general_yml_not_existing_organization_raise_error():
    client = RespoClient()
    with pytest.raises(RespoException):
        client.add_role("test_org_x.test_role_y", validate_input=False)


def test_general_yml_no_validation_role_added_when_no_validation():
    client = RespoClient()
    assert client.add_organization("test_org_x", validate_input=False)
    assert client.add_role("test_org_x.test_role_y", validate_input=False)


def test_general_yml_not_existing_organization_validation_raise_error(
    get_general_model: BaseRespoModel,
):
    respo = get_general_model
    client = RespoClient()
    with pytest.raises(RespoException):
        client.add_organization("test_org_x", respo, validate_input=True)


def test_general_yml_not_existing_organization_no_validation_is_ok():
    client = RespoClient()
    assert client.add_organization("test_org_x", validate_input=False)
