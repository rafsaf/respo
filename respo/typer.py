import json
from pathlib import Path
from typing import Optional

import typer
import yaml
from pydantic import ValidationError
from respo.bin import _save_respo_model, get_respo_model
from respo.respo_model import RespoModel

app = typer.Typer()


def good(s: str) -> str:
    return typer.style(s, fg=typer.colors.GREEN, bold=True)


def info(s: str) -> str:
    return typer.style(s, fg=typer.colors.YELLOW, bold=True)


def bad(s: str) -> str:
    return typer.style(s, fg=typer.colors.WHITE, bg=typer.colors.RED)


@app.command()
def create(
    yml_file: Optional[Path] = typer.Option(
        default=None, help="YML file with resource policy"
    ),
    json_file: Optional[Path] = typer.Option(
        default=None, help="JSON file with resource policy"
    ),
):
    if yml_file is None and json_file is None:
        raise typer.BadParameter("Neither yml_file nor json_file provided")
    elif yml_file is not None and json_file is not None:
        raise typer.BadParameter(
            "Both yml_file and json_file provided, select only one"
        )

    elif yml_file is not None:
        typer.echo(info(f"Processing {yml_file}"))
        if yml_file.is_file():
            try:
                data = yaml.safe_load(yml_file.read_text())
            except yaml.YAMLError as exc:
                typer.echo(exc)
                typer.echo("Could not process yml_file")
                raise typer.Abort()
        elif yml_file.is_dir():
            typer.echo("yml_file is a directory, will use all its yml_file files")
            raise typer.Abort()
        elif not yml_file.exists():
            typer.echo(f"The yml_file {yml_file} doesn't exist")
            raise typer.Abort()
        else:
            typer.echo(f"Unknown path")
            raise typer.Abort()

        try:
            respo_model = RespoModel.parse_obj(data)
        except ValidationError as exc:
            typer.echo(info("Could not validate data"))
            print(exc)
            raise typer.Abort()
        _save_respo_model(respo_model)

    elif json_file is not None:
        typer.echo(f"Processing {json_file}")
        if json_file.is_file():
            try:
                data = json.loads(json_file.read_text())
            except yaml.YAMLError as exc:
                typer.echo(exc)
                typer.echo("Could not process json_file")
                raise typer.Abort()
        elif json_file.is_dir():
            typer.echo("json_file is a directory")
            raise typer.Abort()
        elif not json_file.exists():
            typer.echo(f"The json_file {json_file} doesn't exist")
            raise typer.Abort()
        else:
            typer.echo(f"Unknown path")
            raise typer.Abort()

        respo_model = RespoModel(**data)
        _save_respo_model(respo_model)
    typer.echo(good("Success!"))


@app.command()
def export(
    file: Optional[Path] = typer.Option(
        default=None, help="YML file where respo model will be exported"
    )
):
    if file is None:
        raise typer.BadParameter("file not provided")
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
