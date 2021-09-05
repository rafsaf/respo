import json
from pathlib import Path
from typing import Literal, Optional
from respo.config import config
import typer
import yaml
from pydantic import ValidationError
from respo.bin import _save_respo_model, get_respo_model
from respo.respo_model import RespoModel

app = typer.Typer()


from enum import Enum


class FileFormat(str, Enum):
    yml = "yml"
    json = "json"


def good(s: str) -> str:
    return typer.style("INFO: " + s, fg=typer.colors.GREEN, bold=True)


def bad(s: str) -> str:
    return typer.style("ERROR: " + s, fg=typer.colors.YELLOW, bold=True)


@app.command()
def create(
    file: Path = typer.Argument(..., help="YML file with resource policy"),
    format: FileFormat = typer.Option(
        default="yml", help="JSON file with resource policy"
    ),
):
    typer.echo(good(f"Start looking for file '{file}'"))
    if not file.exists():
        typer.echo(bad(f"The file '{file}' does not exist"))
        raise typer.Abort()
    elif file.is_dir():
        typer.echo(bad(f"The file '{file}' is not a file but a directory"))
        raise typer.Abort()
    elif file.is_file():
        typer.echo(good("Validating the content..."))
        if format.value == "yml":
            try:
                data = yaml.safe_load(file.read_text())
            except yaml.YAMLError as yml_error:
                typer.echo(bad("Could not process file"))
                typer.echo(yml_error)
                raise typer.Abort()
            typer.echo(good("YML syntax is ok..."))
        else:
            try:
                data = json.loads(file.read_text())
            except yaml.YAMLError as json_eror:
                typer.echo(bad("Could not process file"))
                typer.echo(json_eror)
                raise typer.Abort()
            typer.echo(good("JSON syntax is ok..."))
        try:
            respo_model = RespoModel.parse_obj(data)
        except ValidationError as respo_error:
            typer.echo(bad("Could not validate data"))
            typer.echo(respo_error)
            raise typer.Abort()
        typer.echo(good("Respo model syntax is ok..."))
        _save_respo_model(respo_model)
        typer.echo(good(f"Saving as binary file to {config.RESPO_BINARY_FILE_NAME}"))
        typer.echo(good("Success!"))
    else:
        typer.echo(bad(f"File '{file}' is not the text file"))
        typer.Abort()


@app.command()
def export(
    file: Path = typer.Argument(
        default=None, help="YML file where respo model will be exported"
    ),
    format: FileFormat = typer.Option(
        default="yml", help="JSON file with resource policy"
    ),
):
    if file is None:
        path = config.RESPO_DEFAULT_EXPORT_FILE
        if format.value == "yml":
            path += ".yml"
        else:
            path += ".json"
        file = Path(path)

    if file.is_file():
        model = get_respo_model()
        model_dict = model.dict()
        with open(file, "w") as export_file:
            yaml.dump(model_dict, export_file)

    elif file.is_dir():
        typer.echo("file is a directory")
        raise typer.Abort()
    elif not file.exists():
        model = get_respo_model()
        model_dict = model.dict()
        with open(file, "w") as export_file:
            yaml.dump(model_dict, export_file)
    else:
        typer.echo(f"Unknown path")
        raise typer.Abort()
