import typing
import uuid

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import fields
from django.urls import reverse

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
                namespace=self.namespace or getattr(self.model, 'namespace_id', 0),
                extra=self.extra,
            )
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


class IDModel(models.Model):
    # ID namespace, preferably should be different for every model (1 unsigned byte).
    namespace_id = 0  # maybe xor model name or something by default?
    # (Not foolproof but still more variation than default zero everywhere)
    lookup_field = 'uid'  # Not DRY but easier than checking routers every time
    pk_url_kwarg = 'uid'  # Attempt to mimic django class-based views, unfinished
    default_url_namespace = 'api1'
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

    def __str__(self) -> str:
        key = getattr(self, self.lookup_field)
        return f'{self._meta.model_name}: {key}'

    def get_url(self, namespace: str = '') -> str:
        """
        Kinda like the usual get_absolute_url but better.

        Get some values from the model class so we don't have to
        override this for every single new model.
        I like a shorter method name for this and optional argument
        provides forward compatibility with other api versions.
        """
        if not namespace:
            namespace = self.default_url_namespace
        try:
            if namespace:
                # E.g. if namespace=api1 and pattern_name_api1=viewname return api1:viewname
                pattern_name = ':'.join([
                    namespace,
                    getattr(self, f'pattern_name_{namespace}'),
                ])
            else:
                # Not namespaced version, just in case (I like namespaces)
                pattern_name = self.pattern_name
        except AttributeError as exc:
            raise ImproperlyConfigured(exc)
        key = getattr(self, self.lookup_field)
        return reverse(pattern_name, kwargs={self.lookup_field: key})

    def get_absolute_url(self) -> str:
        """
        For compatibility with 3rd-party tools.
        """
        return self.get_url()


class SlugMixin(models.Model):
    """
    Popular additions to many models but not all.
    """
    lookup_field = 'slug'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    name = models.CharField(
        max_length=128,
    )
    slug = models.SlugField(
        max_length=128,
        unique=True,
    )

    class Meta:
        abstract = True
