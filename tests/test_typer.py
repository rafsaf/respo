from pathlib import Path

from typer.testing import CliRunner

from respo import app, BaseRespoModel


def test_respo_create_fail_with_no_file(runner: CliRunner):
    result = runner.invoke(app, ["create"])
    assert result.exit_code == 2
    assert "Missing argument 'FILE'" in result.stdout


def test_respo_create_fail_when_dir(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests"])
    assert result.exit_code == 1
    assert "The file 'tests' is not a file but a directory" in result.stdout


def test_respo_create_fail_when_no_file(runner: CliRunner):
    result = runner.invoke(app, ["create", "some NoT ExisTing File!"])
    assert result.exit_code == 1
    assert "The file 'some NoT ExisTing File!' does not exist" in result.stdout


def test_respo_create_fail_when_yaml_sytax_invalid(runner: CliRunner):
    result = runner.invoke(app, ["create", "tests/cases/other/invalid_yml"])
    assert result.exit_code == 1
    assert "Could not process file" in result.stdout


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


def test_respo_export_success_valid_yml_file(runner: CliRunner, get_general_model):
    result = runner.invoke(app, ["export"])
    result = runner.invoke(app, ["export"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_export_success_valid_json_file(runner: CliRunner, get_general_model):
    result = runner.invoke(app, ["export", "--format", "json"])
    result = runner.invoke(app, ["export", "--format", "json"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout


def test_respo_export_success_valid_yml_custom_name_yml(
    runner: CliRunner, get_general_model
):
    file = "aaa_test_export"
    result = runner.invoke(app, ["export", f"{file}"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    if Path(file).exists():
        Path(file).unlink()


def test_respo_export_success_valid_yml_custom_name_json(
    runner: CliRunner, get_general_model
):
    file = "aaa_test_export"
    result = runner.invoke(app, ["export", f"{file}", "--format", "json"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    if Path(file).exists():
        Path(file).unlink()


def test_respo_export_fail_when_dir(runner: CliRunner):
    result = runner.invoke(app, ["export", "tests"])
    assert result.exit_code == 1
    assert "The file 'tests' is not a file but a directory" in result.stdout


def test_respo_export_fail_respo_error(runner: CliRunner):
    result = runner.invoke(
        app,
        ["export", "tests/cases/invalid/metadata_api_version.yml"],
    )
    assert result.exit_code == 1
    assert "file does not exist. Did you forget to create it?" in result.stdout
