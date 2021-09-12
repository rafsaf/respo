import json
from pathlib import Path
from time import time

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
    file: Path = typer.Argument(..., help="Path to file with resource policy"),
    format: FileFormat = typer.Option(
        default="yml", help="Available format is (default) YML and JSON"
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
                before_yml_time = time()
                data = yaml.safe_load(file.read_text())
                delta_yml_time = round(time() - before_yml_time, 5)
            except yaml.YAMLError as yml_error:
                typer.echo(bad("Could not process file"))
                typer.echo(yml_error)
                raise typer.Abort()
            typer.echo(good(f"YML syntax validated in {delta_yml_time}s..."))
        else:
            try:
                before_json_time = time()
                data = json.loads(file.read_text())
                delta_json_time = round(time() - before_json_time, 5)
            except json.JSONDecodeError as json_eror:
                typer.echo(bad("Could not process file"))
                typer.echo(json_eror)
                raise typer.Abort()
            typer.echo(good(f"JSON syntax validated in {delta_json_time}s..."))
        try:
            before_respo_time = time()
            respo_model = RespoModel.parse_obj(data)
            delta_respo_time = round(time() - before_respo_time, 5)
        except ValidationError as respo_error:
            typer.echo(bad("Could not validate data"))
            typer.echo(respo_error)
            raise typer.Abort()
        typer.echo(good(f"Respo model validated in {delta_respo_time}s..."))
        try:
            old_model = get_respo_model()
        except RespoException:
            pass
        else:
            typer.echo(
                good("Found already created respo model, it will be overwritten")
            )
            respo_model.metadata.created_at = old_model.metadata.created_at

        save_respo_model(respo_model)
        typer.echo(good(f"Saving as binary file to {config.RESPO_BINARY_FILE_NAME}"))
        typer.echo(good("Success!"))


@app.command()
def export(
    file: Path = typer.Argument(
        default=None, help="Path to file where respo model will be exported"
    ),
    format: FileFormat = typer.Option(
        default="yml", help="Available format is (default) YML and JSON"
    ),
):
    if file is None:
        default_path = f"{config.RESPO_DEFAULT_EXPORT_FILE}.{format.value}"
        file = Path(default_path)

    typer.echo(good(f"Start exporting to file '{file}'"))
    if file.exists():
        if file.is_dir():
            typer.echo(bad(f"The file '{file}' is not a file but a directory"))
            raise typer.Abort()
        else:
            typer.echo(good(f"The file '{file}' exists, it will be overwritten"))

    try:
        before_respo_model = time()
        model = get_respo_model()
        delta_respo_model = round(time() - before_respo_model, 5)
    except RespoException as respo_err:
        typer.echo(respo_err)
        raise typer.Abort()
    typer.echo(good(f"Reading respo model took {delta_respo_model}s..."))
    with open(file, "w") as export_file:
        if format == "yml":
            yaml.dump(model.dict(), export_file)
        else:
            json.dump(model.dict(), export_file)
    typer.echo(good(f"Saving as {format} file to {file}"))
    typer.echo(good("Success!"))
