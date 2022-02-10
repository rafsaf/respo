import pytest

from respo import RespoException, RespoModel, RespoClient


def test_general_yml_organization_book123(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_organization("book123", respo)

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


def test_general_yml_organization_default(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_organization("default", respo)

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


def test_general_yml_role_client(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("client", respo)

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


def test_general_yml_role_superuser_book(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("superuser_book", respo)

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


def test_general_yml_role_admin_role(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("admin_role", respo)

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


def test_general_yml_role_test_role(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("test_role", respo)
    client.has_permission("default.test.f", respo)


def test_general_yml_not_existing_permission_label(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("test_role", respo)
    with pytest.raises(RespoException):
        client.has_permission("blabla.blabla.blabla", respo)


def test_general_yml_err_from_not_existing_role_no_force(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("not_existing!!! test_role", respo)
    with pytest.raises(RespoException):
        client.has_permission("default.test.f", respo)


def test_general_yml_no_err_from_not_existing_role_force(get_general_model: RespoModel):
    respo = get_general_model
    client = RespoClient()
    client.add_role("not_existing!!! test_role", respo)
    assert client.has_permission("default.test.f", respo)


def test_general_yml_err_from_not_existing_organization_no_force(
    get_general_model: RespoModel,
):
    respo = get_general_model
    client = RespoClient()
    client.add_organization("default not_existing?!", respo)
    with pytest.raises(RespoException):
        assert client.has_permission("default.test.f", respo)
