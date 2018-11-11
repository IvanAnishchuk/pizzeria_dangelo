"""
Pizza views
"""
import utils.views

import pizzeria_dangelo.pizza.serializers as pizza_serializers
import pizzeria_dangelo.pizza.models as pizza_models


class PizzaViewSet(utils.views.ModelViewSet):
    """
    API endpoint for pizzas

    Nested lookups are prefetched.
    """
    queryset = pizza_models.Pizza.objects.all().order_by('-uid')
    serializer_class = pizza_serializers.PizzaSerializer
    lookup_field = 'slug'


class PizzaSizeViewSet(utils.views.ModelViewSet):
    """
    API endpoint for sizes
    """
    queryset = pizza_models.Size.objects.all().order_by('-uid')
    serializer_class = pizza_serializers.PizzaSizeSerializer
    lookup_field = 'metric'


class PizzaCrustViewSet(utils.views.ModelViewSet):
    """
    API endpoint for crusts
    """
    queryset = pizza_models.Crust.objects.all().order_by('-uid')
    serializer_class = pizza_serializers.PizzaCrustSerializer
    lookup_field = 'slug'


class PizzaToppingViewSet(utils.views.ModelViewSet):
    """
    API endpoint for toppings
    """
    queryset = pizza_models.Topping.objects.all().order_by('-uid')
    serializer_class = pizza_serializers.PizzaToppingSerializer
    lookup_field = 'slug'


class PizzaComponentViewSet(utils.views.ModelViewSet):
    """
    API endpoint for components (Pizza<->Topping through model)
    """
    queryset = pizza_models.PizzaComponent.objects.all().order_by('-uid')
    serializer_class = pizza_serializers.PizzaComponentSerializer
    lookup_field = 'slug'
