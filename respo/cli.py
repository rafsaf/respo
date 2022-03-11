from io import TextIOWrapper
from time import time

import click
import ujson
import yaml
from pydantic import ValidationError

from respo.config import config
from respo.respo_model import RespoError
from respo.respo_model import BaseRespoModel
from respo.save import save_respo_model

from typing import Any, List, Tuple

import click

from respo.config import config
from respo.respo_model import BaseRespoModel, AttributesContainer


def generate_respo_model_file(respo_model: BaseRespoModel) -> None:
    """Generates python file from respo_model.

    Generated file contains class definition that inheritates from
    BaseRespoModel, but with additional typing annotations. It is written
    to config.RESPO_FILE_NAME_RESPO_MODEL.

    Args:
        respo_model: instance of BaseRespoModel

    Returns:
        None
    """
    imports: List[str] = ["BaseRespoModel"]

    def class_definition(item: AttributesContainer, class_name: str):
        result_lst = []
        result_lst.append(f"    class {class_name}:\n")
        if not item.mapping:
            result_lst.append("        pass\n")
        else:
            for name, value in sorted(item.mapping.items()):
                result_lst.append(f"        {name}: {value.__class__.__name__}\n")

        return "".join(result_lst)

    output_text_lst: List[str] = []
    output_text_lst.append('"""\nAuto generated using respo create command\n')
    output_text_lst.append('Docs: https://rafsaf.github.io/respo/\n"""\n\n')

    organization_definition = class_definition(respo_model.ORGS, "ORGS")
    if not organization_definition.endswith("pass\n"):
        imports.append("Organization")

    roles_definition = class_definition(respo_model.ROLES, "ROLES")
    if not roles_definition.endswith("pass\n"):
        imports.append("Role")

    perms_definition = class_definition(respo_model.PERMS, "PERMS")

    output_text_lst.append(f"from respo import {', '.join(imports)}\n\n\n")
    output_text_lst.append("class RespoModel(BaseRespoModel):\n")
    output_text_lst.append(organization_definition)
    output_text_lst.append("\n")
    output_text_lst.append(roles_definition)
    output_text_lst.append("\n")
    output_text_lst.append(perms_definition)

    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "w") as file:
        file.write("".join(output_text_lst))


def good(text: str) -> str:
    """Styles text to green."""

    return click.style(f"INFO: {text}", fg="green", bold=True)


def bad(text: str) -> str:
    """Styles text to yellow."""
    return click.style(f"ERROR: {text}", fg="yellow", bold=True)


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
    and python file with generated model in respo_model.py to improve
    typing support for end user.
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
    except RespoError:
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
