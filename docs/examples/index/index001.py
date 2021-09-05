from respo import create_respo_client, get_respo_model

respo = get_respo_model()
client = create_respo_client(role="foo_admin")

if respo.check("foo.user.read", client):
    pass
