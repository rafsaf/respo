from enum import Enum

import typer

from respo.config import config
from respo.respo_model import BaseRespoModel


class FileFormat(str, Enum):
    yml = "yml"
    json = "json"


def good(s: str) -> str:
    return typer.style("INFO: " + s, fg=typer.colors.GREEN, bold=True)


def bad(s: str) -> str:
    return typer.style("ERROR: " + s, fg=typer.colors.YELLOW, bold=True)


def generate_respo_model_file(respo_model: BaseRespoModel):
    text = ""
    text += '"""\nAuto generated using respo create command\n'
    text += 'Docs: https://rafsaf.github.io/respo/\n"""\n\n'
    text += "from respo import BaseRespoModel, Organization, Role\n\n\n"
    text += "class RespoModel(BaseRespoModel):\n"
    text += "    class ORGS:\n"
    text += "        pass\n"
    orgs = sorted(respo_model.ORGS.__dict__.items(), key=lambda item: item[0])
    for attr_name, _ in orgs:
        if not attr_name.isupper():  # pragma: no cover
            continue
        text += f"        {attr_name}: Organization\n"
    text += "\n"
    text += "    class ROLES:\n"
    text += "        pass\n"
    roles = sorted(respo_model.ROLES.__dict__.items(), key=lambda item: item[0])
    for attr_name, _ in roles:
        if not attr_name.isupper():  # pragma: no cover
            continue
        text += f"        {attr_name}: Role\n"
    text += "\n"
    text += "    class PERMS:\n"
    text += "        pass\n"
    perms = sorted(respo_model.PERMS.__dict__.items(), key=lambda item: item[0])
    for attr_name, _ in perms:
        if not attr_name.isupper():  # pragma: no cover
            continue
        text += f"        {attr_name}: str\n"
    text += "\n"
    text += "    @staticmethod\n"
    text += '    def get_respo_model() -> "RespoModel":\n'
    text += "        return BaseRespoModel.get_respo_model()  # type: ignore\n"

    with open(config.RESPO_FILE_NAME_RESPO_MODEL, "w") as file:
        file.write(text)
