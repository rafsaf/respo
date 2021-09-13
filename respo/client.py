from typing import List, Optional, Union

from pydantic import BaseModel, validator


class Client(BaseModel):
    organizations: List[str]
    roles: List[str]

    @validator("*", pre=True)
    def validate_field(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return v.split()
        return v


def create_respo_client(
    organizations: Optional[Union[List[str], str]] = None,
    roles: Optional[Union[List[str], str]] = None,
):
    return Client(organizations=organizations, roles=roles)
