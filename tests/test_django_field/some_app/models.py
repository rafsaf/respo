from typing import TYPE_CHECKING

from django.db import models

from respo.fields.django import DjangoRespoField


class TheModel(models.Model):
    respo_field = DjangoRespoField()  # type: ignore

    if TYPE_CHECKING:

        @property
        def respo_field(self) -> DjangoRespoField:
            ...
