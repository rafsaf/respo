import pytest

import respo
from tests.test_django_field.some_app.models import ExampleModel


@pytest.mark.django_db
def test_simple_model_creation_and_save():
    respo_client = respo.RespoClient()
    model = ExampleModel(respo_field=respo_client)
    model.save()
    model: ExampleModel = ExampleModel.objects.get(respo_field=respo_client)
    assert model.respo_field.roles == respo_client.roles


@pytest.mark.django_db
def test_field_properly_saved():
    respo_client = respo.RespoClient()
    model = ExampleModel(respo_field=respo_client)
    model.save()
    assert model.respo_field.add_role("xxx123", validate_input=False)
    model.save()
    model: ExampleModel = ExampleModel.objects.get(pk=1)
    assert model.respo_field.roles == ["xxx123"]


@pytest.mark.django_db
def test_field_query():
    respo_client = respo.RespoClient()
    model = ExampleModel(respo_field=respo_client)
    model.save()
    assert model.respo_field.add_role("xxx123", validate_input=False)
    model.save()
    assert ExampleModel.objects.filter(respo_field__icontains="xx123").count()
