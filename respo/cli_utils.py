from typing import Any, List, Tuple

import click

from respo.config import config
from respo.respo_model import BaseRespoModel


def good(s: str) -> str:
    return click.style("INFO: " + s, fg="green", bold=True)


def bad(s: str) -> str:
    return click.style("ERROR: " + s, fg="yellow", bold=True)


def generate_respo_model_file(respo_model: BaseRespoModel):
    def class_part(name: str, annotation: str, lst: List[Tuple[str, Any]]):
        counter = 0
        part = f"    class {name}:\n"
        for attr_name, _ in lst:
            if not attr_name.isupper():  # pragma: no cover
                continue
            part += f"        {attr_name}: {annotation}\n"
            counter += 1
        if not counter:
            part += "        pass\n"
        return part, counter

    text = ""
    text += '"""\nAuto generated using respo create command\n'
    text += 'Docs: https://rafsaf.github.io/respo/\n"""\n\n'

    imports = ["BaseRespoModel"]
    orgs = sorted(respo_model.ORGS.__dict__.items(), key=lambda item: item[0])
    organization_part, o_number = class_part("ORGS", "Organization", orgs)
    if o_number:
        imports.append("Organization")

    roles = sorted(respo_model.ROLES.__dict__.items(), key=lambda item: item[0])
    roles_part, r_number = class_part("ROLES", "Role", roles)
    if r_number:
        imports.append("Role")

    perms = sorted(respo_model.PERMS.__dict__.items(), key=lambda item: item[0])
    perms_part, _ = class_part("PERMS", "str", perms)

    text += f"from respo import {', '.join(imports)}\n\n\n"
    text += "class RespoModel(BaseRespoModel):\n"
    text += organization_part
    text += "\n"
    text += roles_part
    text += "\n"
    text += perms_part
    text += "\n"

    text += "    @staticmethod\n"
    text += '    def get_respo_model() -> "RespoModel":\n'
    text += "        return BaseRespoModel.get_respo_model()  # type: ignore\n"

    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "w") as file:
        file.write(text)
