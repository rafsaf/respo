# main.py - example FastAPI app using respo

from fastapi import FastAPI
from pydantic import BaseModel

from respo import Client, create_respo_client, get_respo_model

app = FastAPI()
respo = get_respo_model()


# You would probably use database, this is just a simple User "table"
class User(BaseModel):
    name: str
    organizations: str = ""
    roles: str = ""

    def respo_client(self) -> Client:
        # ["foo1", "foo2"] or "foo1 foo2" syntax supported
        return create_respo_client(
            roles=self.roles,
            organizations=self.organizations,
        )


@app.get("/{organization}/user_read_all")
async def user_read_all(organization: str):
    user = User(name="user", roles="foo")

    if respo.check(f"{organization}.user.read_all", user.respo_client()):
        return {"message": "Granted!"}

    return {"message": "Denied!"}


@app.get("/{organization}/user_read_basic")
async def user_read_basic(organization: str):
    user = User(name="user", roles="foo")

    if respo.check(f"{organization}.user.read_basic", user.respo_client()):
        return {"message": "Granted!"}

    return {"message": "Denied!"}
