from httpx import AsyncClient


def test_docs_usage_main_roles(get_general_model):
    from docs.examples.usage import main_roles  # noqa


def test_docs_usage_respo_model(get_general_model):

    from docs.examples.usage import respo_model  # noqa


async def test_docs_usage_user_have_permission_I(get_general_model):
    from docs.examples.usage import user_have_permission_I

    async with AsyncClient(
        app=user_have_permission_I.app,
        base_url="http://test",
    ) as client:
        for _ in range(10):
            res = await client.get("/")
            assert res.status_code in [403, 200]
