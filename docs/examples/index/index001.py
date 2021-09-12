# Example endpoint using respo

from fastapi import FastAPI
from pydantic import BaseModel

from respo import create_respo_client, get_respo_model

app = FastAPI()
respo = get_respo_model()


class User(BaseModel):
    name: str
    organizations: list[str] = []
    roles: list[str] = []


@app.get("/")
async def user_read(organization: str):
    me = User(name="user", roles=["foo1", "foo2"])

    client = create_respo_client(
        role=me.roles,
        organization=me.organizations,
    )
    if respo.check(f"{organization}.user.read", client):
        return {"message": "Granted!"}

    return {"message": "Denied!"}
