# main.py

import random

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import Field
from respo import RespoClient

from .respo_model import RespoModel

RESPO_MODEL = RespoModel.get_respo_model()

respo_client_admin = RespoClient()
respo_client_admin.add_role(RESPO_MODEL.ROLES.ADMIN, RESPO_MODEL)
respo_client_no_roles = RespoClient()


fake_users = [
    {"name": "Peter", "respo_field": respo_client_admin},
    {"name": "Sara", "respo_field": respo_client_no_roles},
]


app = FastAPI()


def user_have_permission(permission):
    def inner_user_have_permission():
        # normally we would get user by headers or param etc from
        # another dependency, here we use random user from list
        user = random.choice(fake_users)

        respo_client: RespoClient = user["respo_field"]
        if not respo_client.has_permission(permission, RESPO_MODEL):
            raise HTTPException(403)
        return user

    return inner_user_have_permission


@app.get("/")
def get_all_users(
    user=Depends(user_have_permission(RESPO_MODEL.PERMS.USER__READ_ALL)),
):
    return fake_users
