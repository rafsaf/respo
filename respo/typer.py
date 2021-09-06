import json
from pathlib import Path

import typer
import yaml
from pydantic import ValidationError
from respo.bin import get_respo_model, save_respo_model
from respo.config import config
from respo.helpers import RespoException
from respo.respo_model import RespoModel
from respo.typer_utils import FileFormat, bad, good

app = typer.Typer()


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
    else:
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
            except json.JSONDecodeError as json_eror:
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
        save_respo_model(respo_model)
        typer.echo(good(f"Saving as binary file to {config.RESPO_BINARY_FILE_NAME}"))
        typer.echo(good("Success!"))


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

    typer.echo(good(f"Start exporting to file '{file}'"))
    if file.exists():
        if file.is_dir():
            typer.echo(bad(f"The file '{file}' is not a file but a directory"))
            raise typer.Abort()
        else:
            typer.echo(good(f"The file '{file}' exists, it will be overwritten"))

    try:
        model = get_respo_model()
    except RespoException as respo_err:
        typer.echo(respo_err)
        raise typer.Abort()

    with open(file, "w") as export_file:
        if format == "yml":
            yaml.dump(model.dict(), export_file)
        else:
            json.dump(model.dict(), export_file)
    typer.echo(good(f"Saving as {format} file to {config.RESPO_DEFAULT_EXPORT_FILE}"))
    typer.echo(good("Success!"))
