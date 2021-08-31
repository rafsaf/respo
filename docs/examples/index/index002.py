from respo import get_respo_model, create_respo_client

respo = get_respo_model()
client = create_respo_client(role="user", organization="default")

assert respo.check("foo.user.read_all", client)  # from role
assert respo.check("foo.user.create", client)  # from organization
assert respo.check("foo.user.read_basic", client)  # from 'user.read_all'
