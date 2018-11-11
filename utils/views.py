"""
Customized view base classes and helpers.

A custom exception handler will land here when I'm ready.
"""
import typing

import django.core.exceptions
from django.db.models.query import QuerySet
import django.http
import rest_framework.exceptions
import rest_framework.viewsets
import rest_framework.response


class ModelViewSet(rest_framework.viewsets.ModelViewSet):
    """
    Customized base viewset class

    For now only prefetch automagic is done but can be expanded to do other stuff.
    """

    def get_queryset(self) -> QuerySet:
        """
        Optional queryset prefetching.

        Look for serializer method and use it if present.
        """
        queryset = super().get_queryset()
        if hasattr(self.serializer_class, 'prefetch'):
            return self.serializer_class.prefetch(queryset)
        return queryset


def exception_handler(
        exc: Exception,
        context: typing.Dict[str, typing.Any],  # pylint: disable=unused-argument
) -> typing.Optional[rest_framework.response.Response]:
    """
    Slightly customized exception handler.

    Mainly nicer validation error formatting.
    """
    # Actually context provides some useful stuff
    # but default DRF handler doesn't use it either
    if isinstance(exc, django.http.Http404):
        exc = rest_framework.exceptions.NotFound()
    elif isinstance(exc, django.core.exceptions.PermissionDenied):
        exc = rest_framework.exceptions.PermissionDenied()

    if isinstance(exc, rest_framework.exceptions.APIException):
        headers = {}
        # Inject any other headers perhaps?
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            # Customized: code + detail dictionary instead of just detail
            data = exc.get_full_details()
        else:
            data = {'detail': exc.detail}

        rest_framework.views.set_rollback()
        return rest_framework.response.Response(
            data,
            status=exc.status_code,
            headers=headers,
        )

    # Here we can do something with uncaught exceptions... should we?
    # Since this is an api-first project, some nicer 500 error responses
    # (at least with DEBUG) would probably be helpful for client developers.
    # Consider json-formatted tracebacks with DEBUG=True (would it add any
    # value over plan text?) and simple json error message with DEBUG=False
    # (kinda like the 403 and 404 responses)
    return None
