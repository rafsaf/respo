import pytest
from click.testing import CliRunner

from respo import config
from respo.cli import app
from respo.cli_utils import bad, good


def test_good():
    good_text = "AAA BBB"

    assert good(good_text) == "\x1b[32m\x1b[1mINFO: AAA BBB\x1b[0m"


def test_bad():
    bad_text = "BBB AAA"
    assert bad(bad_text) == "\x1b[33m\x1b[1mERROR: BBB AAA\x1b[0m"


@pytest.mark.parametrize(
    "in_file,out_file",
    [
        ("tests/cases/general.yml", "tests/cases/typer_out_general.py"),
        (
            "tests/cases/valid/minimal_valid_roles.yml",
            "tests/cases/typer_out_minimal_valid_roles.py",
        ),
        (
            "tests/cases/valid/minimal_valid.yml",
            "tests/cases/typer_out_minimal_valid.py",
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
