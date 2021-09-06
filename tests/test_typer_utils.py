from respo.typer_utils import FileFormat, bad, good


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
