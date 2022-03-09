from respo import BaseRespoModel, config
from respo.typer_utils import FileFormat, bad, generate_respo_model_file, good


def test_good():
    good_text = "AAA BBB"

    assert good(good_text) == "\x1b[32m\x1b[1mINFO: AAA BBB\x1b[0m"


def test_bad():
    bad_text = "BBB AAA"
    assert bad(bad_text) == "\x1b[33m\x1b[1mERROR: BBB AAA\x1b[0m"


def test_file_format():
    file_format = FileFormat("yml")
    assert file_format.value == "yml"
    assert file_format.yml == "yml"
    assert file_format.json == "json"


def test_generate_respo_model_file(get_general_model: BaseRespoModel):
    respo = get_general_model
    generate_respo_model_file(respo)
    with open("tests/cases/typer_generated_file.py", "r") as file:
        case_general = file.read()
    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "r") as file:
        generated = file.read()
    assert generated == case_general
