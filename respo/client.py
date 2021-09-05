from typing import List, Optional, Union

from pydantic import BaseModel, validator


class Client(BaseModel):
    organization: List[str]
    role: List[str]

    @validator("*", pre=True)
    def validate_pk(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return v.split()
        return v


def create_respo_client(
    organization: Optional[Union[List[str], str]] = None,
    role: Optional[Union[List[str], str]] = None,
):
    return Client(organization=organization, role=role)
