import typing
import uuid

from django.conf import settings
from django.db import models
from django.db.models import fields

import utils


class IDField(fields.UUIDField, fields.DateTimeCheckMixin):
    """
    A cross of UUIDField and DateTimeField meant to use as a pk.

    Can be auto_now/auto_now_add like DateTimeField, uses UUID
    format like UUIDField and uses a sortable generator for DB efficiency.
    """
    def __init__(
            self, verbose_name: typing.Union[str, None] = None,
            auto_now: bool = False, auto_now_add: bool = False,
            node: int = 0, namespace: int = 0, extra: int = 0,
            **kwargs: typing.Any,
    ):
        self.auto_now, self.auto_now_add = auto_now, auto_now_add
        self.node = node
        self.namespace = namespace
        self.extra = extra
        if auto_now or auto_now_add:
            kwargs['editable'] = False
            kwargs['blank'] = True
        super().__init__(verbose_name, **kwargs)

    def pre_save(self, model_instance: models.Model, add: bool) -> uuid.UUID:
        if self.auto_now or (self.auto_now_add and add):
            value = utils.seq_uuid(
                node=self.node or getattr(settings, 'NODE_ID', 0),
                namespace=self.namespace or getattr(self.model, 'NAMESPACE_ID', 0),
                extra=self.extra,
            )
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)


class IDModel(models.Model):
    uid = IDField(
        auto_now_add=True,
        primary_key=True,
    )
    mid = IDField(
        auto_now=True,
        db_index=True,
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Soft-delete',
    )

    class Meta:
        abstract = True
