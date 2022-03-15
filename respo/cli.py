import io
import json
import os
import pathlib
import pickle
import time
from typing import List, Union
import ast
import click
import pydantic
import ujson
import yaml

from respo import core, settings


def save_respo_model(model: core.RespoModel) -> None:
    """Dumps respo model into bin and yml format files.

    Pickle and yml files are generated and saved to paths specified
    in settings. This behaviour may be overwritten using environment variables.
    """
    pathlib.Path(settings.config.RESPO_AUTO_FOLDER_NAME).mkdir(
        parents=True, exist_ok=True
    )

    with open(settings.config.path_bin_file, "wb") as file:
        pickle.dump(model, file)

    with open(settings.config.path_yml_file, mode="w") as file:  # type: ignore
        yaml.dump(model, file)


def generate_respo_model_file(respo_model: core.RespoModel) -> None:
    """Generates python file with class RespoModel.

    Generated file contains class definition that inheritates from
    RespoModel, but with additional typing annotations. It is written
    to config.RESPO_FILE_NAME_RESPO_MODEL.
    """

    def class_definition(
        labels_container: Union[core.ROLESContainer, core.PERMSContainer],
        class_name: str,
    ):
        result_lst = []
        result_lst.append(f"        class {class_name}:\n")
        if not len(labels_container):
            result_lst.append("            pass\n")
        else:
            for name in sorted(
                label for label in labels_container.__dict__ if label.isupper()
            ):
                result_lst.append(f"            {name}: str\n")
        result_lst.append("\n")
        return "".join(result_lst)

    output_text_lst: List[str] = []
    output_text_lst.append('"""\nAuto generated using respo create command\n')
    output_text_lst.append('Docs: https://rafsaf.github.io/respo/\n"""\n\n')

    roles_definition = class_definition(respo_model.ROLES, "ROLES")

    perms_definition = class_definition(respo_model.PERMS, "PERMS")

    output_text_lst.append("import respo\n")
    output_text_lst.append("import typing\n\n\n")
    output_text_lst.append("class RespoModel(respo.RespoModel):\n")
    output_text_lst.append("    if typing.TYPE_CHECKING:\n\n")
    output_text_lst.append(roles_definition)
    output_text_lst.append(perms_definition)
    output_text_lst.append("        @staticmethod\n")
    output_text_lst.append('        def get_respo_model() -> "RespoModel":\n')
    output_text_lst.append(
        "            return respo.RespoModel.get_respo_model()  # type: ignore\n"
    )

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


@click.option("--no-json-preview", is_flag=True, type=bool, default=False)
@click.option("--no-python-file", is_flag=True, type=bool, default=False)
@click.argument("file", type=click.File("r"))
@app.command()
def create(
    file: io.TextIOWrapper,
    no_json_preview: bool,
    no_python_file: bool,
):
    """Parses FILENAME with declared respo resource policies.

    Creates pickled model representation by default in .respo_cache folder
    and python file with generated model in respo_model.py to improve
    typing support for end user.
    """

    click.echo(good(f"Validating respo model from {file.name}..."))
    start_time = time.time()
    try:
        data = yaml.safe_load(file.read())
        respo_model = core.RespoModel.parse_obj(data)
    except yaml.YAMLError as yml_error:
        click.echo(f"\n{yml_error}\n")
        click.echo(bad("Could not process file, yml syntax is invalid"))
        raise click.Abort()
    except pydantic.ValidationError as respo_errors:
        errors = [
            error
            for error in respo_errors.errors()
            if error["type"] != "assertion_error"  # theese are unuseful errors
        ]
        for error in errors:
            if error["type"] == "value_error.respomodel":
                loc_msg = error["msg"].split("|")
                error["loc"] = ast.literal_eval(loc_msg[0])
                error["msg"] = loc_msg[1]
        no_errors = len(errors)
        click.echo(bad("Could not validate respo model"))
        click.echo(
            bad(
                f'Found {no_errors} validation error{"" if no_errors == 1 else "s"} for RespoModel\n\n'
            )
            + f"{pydantic.error_wrappers.display_errors(errors)}\n"
        )
        raise click.Abort()

    save_respo_model(respo_model)
    if not no_python_file:
        generate_respo_model_file(respo_model=respo_model)
    if not no_json_preview:
        with open(settings.config.path_json_file, "w") as file:
            json.dump(respo_model.roles_permissions, file, indent=4)

    click.echo(good(f"Saved binary file to {settings.config.path_bin_file}"))
    click.echo(good(f"Saved yml file to {settings.config.path_yml_file}"))
    click.echo(good(f"Saved python file to {settings.config.path_python_file}"))

    process_time = round(time.time() - start_time, 4)
    bin_file_size = round(os.path.getsize(settings.config.path_bin_file) / 1048576, 4)
    click.echo(
        good(f"Processed in {process_time}s. Bin file size: {bin_file_size} mb.")
    )
    click.echo(good("Success!"))
