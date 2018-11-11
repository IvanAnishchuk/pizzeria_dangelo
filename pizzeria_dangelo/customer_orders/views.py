"""
Order views
"""
import utils.views

import pizzeria_dangelo.customer_orders.serializers
import pizzeria_dangelo.customer_orders.models as orders_models


class OrderViewSet(utils.views.ModelViewSet):
    """
    API endpoint for pizzas
    """
    queryset = orders_models.Order.objects.all().order_by('-uid')
    serializer_class = pizzeria_dangelo.customer_orders.serializers.OrderSerializer
    lookup_field = 'uid'
