"""
Extras views
"""
import utils.views

import pizzeria_dangelo.extras.serializers
import pizzeria_dangelo.extras.models as extras_models


class ExtraViewSet(utils.views.ModelViewSet):
    """
    API endpoint for extras
    """
    queryset = extras_models.Extra.objects.all().order_by('-uid')
    serializer_class = pizzeria_dangelo.extras.serializers.ExtraSerializer
    lookup_field = 'slug'


class ExtraCategoryViewSet(utils.views.ModelViewSet):
    """
    API endpoint for categories
    """
    queryset = extras_models.ExtraCategory.objects.all().order_by('-uid')
    serializer_class = pizzeria_dangelo.extras.serializers.ExtraCategorySerializer
    lookup_field = 'slug'
