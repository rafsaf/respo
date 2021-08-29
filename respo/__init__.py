from typing import Dict, Optional, Any
from respo.resource_policy import get_respo_model, create_respo_client
from respo.helpers import ResourcePolicyException, logger
from respo.resource_model import ResourceModel


if __name__ == "__main__":
    respo = get_respo_model(path_to_yml="../tests/my_resource_policy.yml")

    client = create_respo_client(pk="5", organization="default", role="superuser")
    respo.check("all.user.all", client)
