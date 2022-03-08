from enum import Enum

import typer

from respo.config import config
from respo.respo_model import RespoModel


class FileFormat(str, Enum):
    yml = "yml"
    json = "json"


def good(s: str) -> str:
    return typer.style("INFO: " + s, fg=typer.colors.GREEN, bold=True)


def bad(s: str) -> str:
    return typer.style("ERROR: " + s, fg=typer.colors.YELLOW, bold=True)


def generate_respo_model_file(respo_model: RespoModel):
    text = ""
    text += '"""\nAuto generated using respo create command\n'
    text += 'Docs: https://rafsaf.github.io/respo/\n"""\n\n'
    text += (
        "from respo import Organization, Role, RespoModel as OriginalRespoModel\n\n\n"
    )
    text += "class RespoModel(OriginalRespoModel):\n"
    text += "    class ORGS:\n"
    for attr_name in respo_model.ORGS.__dict__:
        if not attr_name.isupper():
            continue
        text += f"        {attr_name}: Organization\n"
    text += "\n"
    text += "    class ROLES:\n"
    for attr_name in respo_model.ROLES.__dict__:
        if not attr_name.isupper():
            continue
        text += f"        {attr_name}: Role\n"
    text += "\n"
    text += "    class PERMS:\n"
    for attr_name in respo_model.PERMS.__dict__:
        if not attr_name.isupper():
            continue
        text += f"        {attr_name}: str\n"
    text += "\n"
    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "w") as file:
        file.write(text)
