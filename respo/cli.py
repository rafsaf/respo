from io import TextIOWrapper
from time import time

import click
import ujson
import yaml
from pydantic import ValidationError

from respo.cli_utils import bad, generate_respo_model_file, good
from respo.config import config
from respo.helpers import RespoException
from respo.respo_model import BaseRespoModel
from respo.save import save_respo_model


@click.group()
def app():
    pass


@click.argument("file", type=click.File("r"))
@click.option(
    "--format", type=click.Choice(["yml", "json"], case_sensitive=False), default="yml"
)
@app.command()
def create(file: TextIOWrapper, format: str):
    """
    Parse FILENAME with declared respo resource policies.
    Creates pickled model representation by default in .respo_cache folder
    and python file with generated model in respo_model.py
    """

    click.echo(good("Validating the content..."))
    before = time()
    try:
        if format == "yml":
            data = yaml.safe_load(file.read())
        else:
            data = ujson.load(file)
        respo_model = BaseRespoModel.parse_obj(data)
    except yaml.YAMLError as yml_error:
        click.echo(bad("Could not process file, yml syntax is invalid"))
        click.echo(yml_error)
        raise click.Abort()
    except ValidationError as respo_error:
        click.echo(bad("Could not validate respo model"))
        click.echo(respo_error)
        raise click.Abort()
    except ValueError as json_eror:
        click.echo(bad("Could not process file, json syntax is invalid"))
        click.echo(json_eror)
        raise click.Abort()
    except Exception as err:  # pragma: no cover
        click.echo(bad(f"Unexpected error when processing this file. {err}"))
        raise click.Abort()
    else:
        delta = round(time() - before, 5)
        click.echo(good(f"Respo model validated in {delta}s..."))
    try:
        old_model = BaseRespoModel.get_respo_model()
    except RespoException:
        pass
    else:
        click.echo(good("Found already created respo model, it will be overwritten"))
        respo_model.metadata.created_at = old_model.metadata.created_at

    save_respo_model(respo_model)
    click.echo(
        good(
            "Saving as binary file to "
            f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_BINARY_FILE_NAME}"
        )
    )
    click.echo(
        good(
            "Saving as yml file to "
            f"{config.RESPO_AUTO_FOLDER_NAME}/{config.RESPO_AUTO_YML_FILE_NAME}"
        )
    )
    click.echo(good("Generating respo model file..."))
    generate_respo_model_file(respo_model=respo_model)
    click.echo(good(f"Saving as python file to {config.RESPO_FILE_NAME_RESPO_MODEL}"))
    click.echo(good("Success!"))
