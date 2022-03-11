from click.testing import CliRunner
import pytest
from respo import BaseRespoModel, config
from respo.cli import app, good, bad


def test_good():
    good_text = "AAA BBB"

    assert good(good_text) == "\x1b[32m\x1b[1mINFO: AAA BBB\x1b[0m"


def test_bad():
    bad_text = "BBB AAA"
    assert bad(bad_text) == "\x1b[33m\x1b[1mERROR: BBB AAA\x1b[0m"


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
def test_generate_respo_model_file(runner: CliRunner, in_file: str, out_file: str):
    runner.invoke(app, ["create", in_file])
    with open(out_file, "r") as file:
        case = file.read()
    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "r") as file:
        generated = file.read()
    assert generated == case


def test_respo_create_fail_with_no_file(runner: CliRunner):
    result = runner.invoke(app, ["create"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stdout


def test_respo_create_fail_when_dir(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests"])
    assert result.exit_code == 2
    assert "Is a directory" in result.stdout


def test_respo_create_fail_when_no_file(runner: CliRunner):
    result = runner.invoke(app, ["create", "some NoT ExisTing File!"])
    assert result.exit_code == 2
    assert "No such file or directory" in result.stdout


def test_respo_create_fail_when_yaml_sytax_invalid(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests/cases/other/invalid_yml"])
    assert result.exit_code == 1
    assert "Could not process file" in result.stdout


def test_respo_create_fail_when_yaml_sytax_valid_but_broken(runner: CliRunner):
    result = runner.invoke(
        app, ["create", "tests/cases/invalid/metadata_created_at.yml"]
    )
    assert result.exit_code == 1
    assert "Could not validate respo model" in result.stdout


def test_respo_create_fail_when_json_sytax_invalid(runner: CliRunner):
    result = runner.invoke(
        app, ["create", "tests/cases/other/invalid_json", "--format", "json"]
    )
    assert result.exit_code == 1
    assert "Could not process file" in result.stdout


def test_respo_create_success_valid_yml_file(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests/cases/general.yml"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_create_success_valid_yml_file_2x_modify_created_ok(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests/cases/general.yml"])
    model1 = BaseRespoModel.get_respo_model()
    result = runner.invoke(app, ["create", "tests/cases/general.yml"])
    model2 = BaseRespoModel.get_respo_model()
    assert model1.metadata.created_at == model2.metadata.created_at
    assert not model1.metadata.last_modified == model2.metadata.last_modified
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_create_success_valid_json_file(runner: CliRunner):
    result = runner.invoke(
        app, ["create", "tests/cases/general.json", "--format", "json"]
    )
    assert result.exit_code == 0
    assert "Success!" in result.stdout
