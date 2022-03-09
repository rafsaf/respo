from pathlib import Path
from time import time

import typer
import ujson
import yaml
from pydantic import ValidationError

from respo.bin import save_respo_model
from respo.config import config
from respo.helpers import RespoException
from respo.respo_model import BaseRespoModel
from respo.typer_utils import FileFormat, bad, generate_respo_model_file, good

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
            except Exception:  # pragma: no cover
                typer.echo(bad("Unexpected error when processing yml."))
                raise typer.Abort()
            typer.echo(good(f"YML syntax validated in {delta_yml_time}s..."))
        else:
            try:
                before_json_time = time()
                data = ujson.loads(file.read_text())
                delta_json_time = round(time() - before_json_time, 5)
            except ValueError as json_eror:
                typer.echo(bad("Could not process file"))
                typer.echo(json_eror)
                raise typer.Abort()
            except Exception:  # pragma: no cover
                typer.echo(bad("Unexpected error when processing json."))
                raise typer.Abort()
            typer.echo(good(f"JSON syntax validated in {delta_json_time}s..."))
        try:
            before_respo_time = time()
            respo_model = BaseRespoModel.parse_obj(data)
            delta_respo_time = round(time() - before_respo_time, 5)
        except ValidationError as respo_error:
            typer.echo(bad("Could not validate data"))
            typer.echo(respo_error)
            raise typer.Abort()
        typer.echo(good(f"Respo model validated in {delta_respo_time}s..."))
        try:
            old_model = BaseRespoModel.get_respo_model()
        except RespoException:
            pass
        else:
            typer.echo(
                good("Found already created respo model, it will be overwritten")
            )
            respo_model.metadata.created_at = old_model.metadata.created_at

        save_respo_model(respo_model)
        typer.echo(
            good(
                f"Saving as binary file to {config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}"
            )
        )
        typer.echo(
            good(
                f"Saving as yml file to {config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_YML_FILE_NAME}"
            )
        )
        typer.echo(good("Generating respo model file..."))
        generate_respo_model_file(respo_model=respo_model)
        typer.echo(good(f"Saving as py file to {config.RESPO_FILE_NAME_RESPO_MODEL}"))
        typer.echo(good("Success!"))


@app.command()
def future():  # pragma: no cover
    pass
