from enum import Enum

import typer


class FileFormat(str, Enum):
    yml = "yml"
    json = "json"


def good(s: str) -> str:
    return typer.style("INFO: " + s, fg=typer.colors.GREEN, bold=True)


def bad(s: str) -> str:
    return typer.style("ERROR: " + s, fg=typer.colors.YELLOW, bold=True)
