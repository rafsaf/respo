import pytest

from respo import RespoException, RespoModel, create_respo_client


def test_general_yml_organization_book123(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(organizations="book123")

    assert respo.check("book123.user.read_basic", client)
    assert not respo.check("book123.user.all", client)
    assert not respo.check("book123.user.read_all", client)
    assert not respo.check("book123.user.read_all_better", client)
    assert not respo.check("book123.user.update", client)
    assert not respo.check("book123.user.delete", client)

    assert respo.check("book123.book.list", client)
    assert respo.check("book123.book.read", client)
    assert respo.check("book123.book.buy_all", client)
    assert respo.check("book123.book.buy", client)
    assert not respo.check("book123.book.sell", client)

    assert not respo.check("default.user.read_basic", client)
    assert not respo.check("default.user.all", client)
    assert not respo.check("default.user.read_all", client)
    assert not respo.check("default.user.read_all_better", client)
    assert not respo.check("default.user.update", client)
    assert not respo.check("default.user.delete", client)

    assert not respo.check("default.book.list", client)
    assert not respo.check("default.book.read", client)
    assert not respo.check("default.book.buy_all", client)
    assert not respo.check("default.book.buy", client)
    assert not respo.check("default.book.sell", client)


def test_general_yml_organization_default(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(organizations="default")

    assert not respo.check("book123.user.read_basic", client)
    assert not respo.check("book123.user.all", client)
    assert not respo.check("book123.user.read_all", client)
    assert not respo.check("book123.user.read_all_better", client)
    assert not respo.check("book123.user.update", client)
    assert not respo.check("book123.user.delete", client)

    assert not respo.check("book123.book.list", client)
    assert not respo.check("book123.book.read", client)
    assert not respo.check("book123.book.buy_all", client)
    assert not respo.check("book123.book.buy", client)
    assert not respo.check("book123.book.sell", client)

    assert respo.check("default.user.read_basic", client)
    assert not respo.check("default.user.all", client)
    assert respo.check("default.user.read_all", client)
    assert respo.check("default.user.read_all_better", client)
    assert not respo.check("default.user.update", client)
    assert not respo.check("default.user.delete", client)

    assert not respo.check("default.book.list", client)
    assert not respo.check("default.book.read", client)
    assert not respo.check("default.book.buy_all", client)
    assert not respo.check("default.book.buy", client)
    assert not respo.check("default.book.sell", client)


def test_general_yml_role_client(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="client")

    assert respo.check("book123.user.read_basic", client)
    assert not respo.check("book123.user.all", client)
    assert not respo.check("book123.user.read_all", client)
    assert not respo.check("book123.user.read_all_better", client)
    assert not respo.check("book123.user.update", client)
    assert not respo.check("book123.user.delete", client)

    assert respo.check("book123.book.list", client)
    assert respo.check("book123.book.read", client)
    assert respo.check("book123.book.buy_all", client)
    assert respo.check("book123.book.buy", client)
    assert not respo.check("book123.book.sell", client)

    assert not respo.check("default.user.read_basic", client)
    assert not respo.check("default.user.all", client)
    assert not respo.check("default.user.read_all", client)
    assert not respo.check("default.user.read_all_better", client)
    assert not respo.check("default.user.update", client)
    assert not respo.check("default.user.delete", client)

    assert not respo.check("default.book.list", client)
    assert not respo.check("default.book.read", client)
    assert not respo.check("default.book.buy_all", client)
    assert not respo.check("default.book.buy", client)
    assert not respo.check("default.book.sell", client)


def test_general_yml_role_superuser_book(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="superuser_book")

    assert respo.check("book123.user.read_basic", client)
    assert respo.check("book123.user.all", client)
    assert respo.check("book123.user.read_all", client)
    assert respo.check("book123.user.read_all_better", client)
    assert respo.check("book123.user.update", client)
    assert respo.check("book123.user.delete", client)

    assert respo.check("book123.book.list", client)
    assert respo.check("book123.book.read", client)
    assert respo.check("book123.book.buy_all", client)
    assert respo.check("book123.book.buy", client)
    assert not respo.check("book123.book.sell", client)

    assert not respo.check("default.user.read_basic", client)
    assert not respo.check("default.user.all", client)
    assert not respo.check("default.user.read_all", client)
    assert not respo.check("default.user.read_all_better", client)
    assert not respo.check("default.user.update", client)
    assert not respo.check("default.user.delete", client)

    assert not respo.check("default.book.list", client)
    assert not respo.check("default.book.read", client)
    assert not respo.check("default.book.buy_all", client)
    assert not respo.check("default.book.buy", client)
    assert not respo.check("default.book.sell", client)


def test_general_yml_role_admin_role(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="admin_role")

    assert respo.check("book123.user.read_basic", client)
    assert not respo.check("book123.user.all", client)
    assert respo.check("book123.user.read_all", client)
    assert not respo.check("book123.user.read_all_better", client)
    assert not respo.check("book123.user.update", client)
    assert not respo.check("book123.user.delete", client)

    assert respo.check("book123.book.list", client)
    assert respo.check("book123.book.read", client)
    assert respo.check("book123.book.buy_all", client)
    assert respo.check("book123.book.buy", client)
    assert respo.check("book123.book.sell", client)

    assert not respo.check("default.user.read_basic", client)
    assert not respo.check("default.user.all", client)
    assert not respo.check("default.user.read_all", client)
    assert not respo.check("default.user.read_all_better", client)
    assert not respo.check("default.user.update", client)
    assert not respo.check("default.user.delete", client)

    assert not respo.check("default.book.list", client)
    assert not respo.check("default.book.read", client)
    assert not respo.check("default.book.buy_all", client)
    assert not respo.check("default.book.buy", client)
    assert not respo.check("default.book.sell", client)


def test_general_yml_role_test_role(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="test_role")
    assert respo.check("default.test.f", client)


def test_general_yml_not_existing_permission_label(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="test_role")
    with pytest.raises(RespoException):
        respo.check("blabla.blabla.blabla", client=client)


def test_general_yml_err_from_not_existing_role_no_force(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="not_existing!!! test_role")
    with pytest.raises(RespoException):
        respo.check("default.test.f", client)
    with pytest.raises(RespoException):
        respo.check("default.test.f", client, force=False)


def test_general_yml_no_err_from_not_existing_role_force(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="not_existing!!! test_role")

    assert respo.check("default.test.f", client, force=True)


def test_general_yml_err_from_not_existing_organization_no_force(
    get_general_model: RespoModel,
):
    respo = get_general_model
    client = create_respo_client(organizations="default not_existing?!")
    with pytest.raises(RespoException):
        respo.check("default.test.f", client)
    with pytest.raises(RespoException):
        respo.check("default.test.f", client, force=False)


def test_general_yml_no_err_from_not_existing_organization_force(
    get_general_model: RespoModel,
):
    respo = get_general_model
    client = create_respo_client(organizations="default not_existing?!")

    assert respo.check("default.user.read_basic", client, force=True)


def test_default_root_is_ok(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(roles="root.default")

    assert respo.check("default.user.read_basic", client)
    assert respo.check("default.user.all", client)
    assert respo.check("default.user.read_all", client)
    assert respo.check("default.user.read_all_better", client)
    assert respo.check("default.user.update", client)
    assert respo.check("default.user.delete", client)

    assert respo.check("default.book.list", client)
    assert respo.check("default.book.read", client)
    assert respo.check("default.book.buy_all", client)
    assert respo.check("default.book.buy", client)
    assert respo.check("default.book.sell", client)
