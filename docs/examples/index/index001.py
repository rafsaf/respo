from respo import get_respo_model, create_respo_client

respo = get_respo_model()
client = create_respo_client(role="foo_admin")

if respo.check("foo.user.read", client):
    pass
