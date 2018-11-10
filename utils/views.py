"""
Customized view base classes and helpers.

A custom exception handler will land here when I'm ready.
"""

import rest_framework.viewsets


class ModelViewSet(rest_framework.viewsets.ModelViewSet):
    """
    Customized base viewset class

    For now only prefetch automagic is done but can be expanded to do other stuff.
    """

    def get_queryset(self):
        """
        Optional queryset prefetching.

        Look for serializer method and use it if present.
        TODO: Do we actually need a method or a list of fields could be enough?
        """
        queryset = super().get_queryset()
        if hasattr(self.serializer_class, 'prefetch'):
            return self.serializer_class.prefetch(queryset)
        else:
            return queryset
