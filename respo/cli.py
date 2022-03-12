import io
import os
import pathlib
import pickle
import time
from typing import List

import click
import pydantic
import ujson
import yaml

from respo import core, exceptions, settings


def save_respo_model(model: core.RespoModel) -> None:
    """Dumps respo model into bin and yml format.

    Pickle and yml files are generated and saved to paths specified
    in respo.config. This behaviour may be overwritten using ENV variables.
    """
    pathlib.Path(settings.config.RESPO_AUTO_FOLDER_NAME).mkdir(
        parents=True, exist_ok=True
    )

    with open(settings.config.path_bin_file, "wb") as file:
        pickle.dump(model, file)

    with open(settings.config.path_yml_file, mode="w") as file:  # type: ignore
        yaml.dump(
            model.dict(
                exclude={
                    "permission_to_organization_dict",
                    "permission_to_role_dict",
                    "PERMS",
                    "ORGS",
                    "ROLES",
                }
            ),
            file,
        )


def generate_respo_model_file(respo_model: core.RespoModel) -> None:
    """Generates python file from respo_model.

    Generated file contains class definition that inheritates from
    RespoModel, but with additional typing annotations. It is written
    to config.RESPO_FILE_NAME_RESPO_MODEL.
    """
    imports: List[str] = ["RespoModel"]

    def class_definition(item: core.AttributesContainer, class_name: str):
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
    output_text_lst.append("class RespoModel(RespoModel):\n")
    output_text_lst.append(organization_definition)
    output_text_lst.append("\n")
    output_text_lst.append(roles_definition)
    output_text_lst.append("\n")
    output_text_lst.append(perms_definition)

    with open(settings.config.RESPO_FILE_NAME_RESPO_MODEL, "w") as file:
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
def create(file: io.TextIOWrapper, format: str):
    """
    Parse FILENAME with declared respo resource policies.
    Creates pickled model representation by default in .respo_cache folder
    and python file with generated model in respo_model.py to improve
    typing support for end user.
    """

    click.echo(good(f"Validating respo model from {file.name}..."))
    start_time = time.time()
    try:
        if format == "yml":
            data = yaml.safe_load(file.read())
        else:
            data = ujson.load(file)
        respo_model = core.RespoModel.parse_obj(data)
    except yaml.YAMLError as yml_error:
        click.echo(bad("Could not process file, yml syntax is invalid"))
        click.echo(yml_error)
        raise click.Abort()
    except pydantic.ValidationError as respo_error:
        click.echo(bad("Could not validate respo model"))
        click.echo(respo_error)
        raise click.Abort()
    except ValueError as json_eror:
        click.echo(bad("Could not process file, json syntax is invalid"))
        click.echo(json_eror)
        raise click.Abort()
    try:
        old_model = core.RespoModel.get_respo_model()
    except exceptions.RespoModelError:
        pass
    else:
        respo_model.metadata.created_at = old_model.metadata.created_at
        click.echo(good("Existing model updated."))

    save_respo_model(respo_model)
    generate_respo_model_file(respo_model=respo_model)

    click.echo(good(f"Saved binary file to {settings.config.path_bin_file}"))
    click.echo(good(f"Saved yml file to {settings.config.path_yml_file}"))
    click.echo(good(f"Saved python file to {settings.config.path_python_file}"))

    process_time = round(time.time() - start_time, 4)
    bin_file_size = round(os.path.getsize(settings.config.path_bin_file) / 1048576, 4)
    click.echo(
        good(f"Processed in {process_time}s. Bin file size: {bin_file_size} mb.")
    )
    click.echo(good("Success!"))
