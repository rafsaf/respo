import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from respo import app


def test_respo_example_yml_isvalid(runner: CliRunner):
    result = runner.invoke(app, ["create", "docs/examples/index/respo-example.yml"])
    assert "Success!" in result.stdout


@pytest.fixture
def client(runner: CliRunner):
    runner.invoke(app, ["create", "docs/examples/index/respo-example.yml"])
    from docs.examples.index.index001 import app as fastapi_app

    client = TestClient(fastapi_app)
    return client


def test_index001_first_endpoint_true(client: TestClient):
    response = client.get("/default/user_read_all")
    assert response.status_code == 200
    assert response.json() == {"message": "Granted!"}


def test_index001_first_endpoint_false(client: TestClient):
    response = client.get("/other/user_read_all")
    assert response.status_code == 200
    assert response.json() == {"message": "Denied!"}


def test_index001_second_endpoint_true(client: TestClient):
    response = client.get("/default/user_read_basic")
    assert response.status_code == 200
    assert response.json() == {"message": "Granted!"}


def test_index001_second_endpoint_false(client: TestClient):
    response = client.get("/other/user_read_basic")
    assert response.status_code == 200
    assert response.json() == {"message": "Denied!"}
