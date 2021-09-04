from respo import RespoModel, create_respo_client
import os

os.environ["RESPO_BINARY_FILE_NAME"] = "test_respo.general.yml.bin"


def test_general_yml_organization_book123(get_general_model: RespoModel):
    respo = get_general_model
    client = create_respo_client(organization="book123")

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
    client = create_respo_client(organization="default")

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
    client = create_respo_client(role="client")

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
    client = create_respo_client(role="superuser_book")

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
    client = create_respo_client(role="admin_role")

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
