from typing import Any, List, Tuple

import click

from respo.config import config
from respo.respo_model import BaseRespoModel, AttributesContainer


def good(text: str) -> str:
    """Styles text to green."""

    return click.style(f"INFO: {text}", fg="green", bold=True)


def bad(text: str) -> str:
    """Styles text to yellow."""
    return click.style(f"ERROR: {text}", fg="yellow", bold=True)


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
