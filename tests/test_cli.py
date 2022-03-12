import pytest
from click import testing

import respo
from respo import cli
from tests import conftest


def test_model_is_equal_after_dumping():
    model1 = conftest.get_model("tests/cases/general.yml")
    cli.save_respo_model(model1)
    model2 = respo.RespoModel.get_respo_model()
    assert model1 == model2


def test_good():
    good_text = "AAA BBB"

    assert cli.good(good_text) == "\x1b[32m\x1b[1mINFO: AAA BBB\x1b[0m"


def test_bad():
    bad_text = "BBB AAA"
    assert cli.bad(bad_text) == "\x1b[33m\x1b[1mERROR: BBB AAA\x1b[0m"


@pytest.mark.parametrize(
    "in_file,out_file",
    [
        ("tests/cases/general.yml", "tests/cases/click_out_general.py"),
        (
            "tests/cases/valid/minimal_valid_roles.yml",
            "tests/cases/click_out_minimal_valid_roles.py",
        ),
        (
            "tests/cases/valid/minimal_valid.yml",
            "tests/cases/click_out_minimal_valid.py",
        ),
    ],
)
def test_generate_respo_model_file(
    runner: testing.CliRunner, in_file: str, out_file: str
):
    runner.invoke(cli.app, ["create", in_file])
    with open(out_file, "r") as file:
        case = file.read()
    with open(respo.config.RESPO_FILE_NAME_RESPO_MODEL, "r") as file:
        generated = file.read()
    assert generated == case


def test_respo_create_fail_with_no_file(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stdout


def test_respo_create_fail_when_dir(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create", "tests"])
    assert result.exit_code == 2
    assert "Is a directory" in result.stdout


def test_respo_create_fail_when_no_file(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create", "some NoT ExisTing File!"])
    assert result.exit_code == 2
    assert "No such file or directory" in result.stdout


def test_respo_create_fail_when_yaml_sytax_invalid(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create", "tests/cases/other/invalid_yml"])
    assert result.exit_code == 1
    assert "Could not process file" in result.stdout


def test_respo_create_fail_when_yaml_sytax_valid_but_invalid_model(
    runner: testing.CliRunner,
):
    result = runner.invoke(
        cli.app, ["create", "tests/cases/invalid/metadata_created_at.yml"]
    )
    assert result.exit_code == 1
    assert "Could not validate respo model" in result.stdout


def test_respo_create_fail_when_json_sytax_invalid(runner: testing.CliRunner):
    result = runner.invoke(
        cli.app, ["create", "tests/cases/other/invalid_json", "--format", "json"]
    )
    assert result.exit_code == 1
    assert "Could not process file" in result.stdout


def test_respo_create_success_valid_yml_file(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create", "tests/cases/general.yml"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_create_success_valid_yml_file_2x_modify_ok(runner: testing.CliRunner):
    result = runner.invoke(cli.app, ["create", "tests/cases/general.yml"])
    model1 = respo.RespoModel.get_respo_model()
    result = runner.invoke(cli.app, ["create", "tests/cases/general.yml"])
    model2 = respo.RespoModel.get_respo_model()
    assert model1.metadata.created_at == model2.metadata.created_at
    assert not model1.metadata.last_modified == model2.metadata.last_modified
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_create_success_valid_json_file(runner: testing.CliRunner):
    result = runner.invoke(
        cli.app, ["create", "tests/cases/general.json", "--format", "json"]
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout
