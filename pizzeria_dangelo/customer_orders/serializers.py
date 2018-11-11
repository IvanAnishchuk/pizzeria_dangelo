from django.db.models.query import QuerySet
import drf_writable_nested
from rest_framework import serializers

import pizzeria_dangelo.customer_orders.models as orders_models
import pizzeria_dangelo.pizza.models as pizza_models
import pizzeria_dangelo.extras.models as extras_models


class OrderComponentSerializer(serializers.HyperlinkedModelSerializer):
    """
    Nested serializer, we don't have a separate endpoint for this.
    """

    class Meta:
        model = orders_models.OrderComponent
        fields = ['uid', 'mid', 'component', 'amount']
        extra_kwargs = {
            'component': {
                'view_name': 'api1:pizzacomponent-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.PizzaComponent.objects.all(),
            },
        }


class OrderItemSerializer(
        drf_writable_nested.mixins.NestedCreateMixin,
        drf_writable_nested.mixins.NestedUpdateMixin,
        serializers.HyperlinkedModelSerializer,
):
    """
    This one does most of the custom validation.

    As Item objects are polymorph (could be either pizza with options or an
    extra) we mark all fields as non-required and check the requirements
    in validate method here instead. Might be imperfect but works.
    The alternative would be to use related queryset filtering or validators
    but this way is much simpler even if results in some more code.
    """
    components = OrderComponentSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = orders_models.OrderItem
        fields = [
            'uid', 'mid',
            'pizza', 'size', 'crust',
            'components', 'amount',
            'extra',
        ]
        extra_kwargs = {
            'pizza': {
                'view_name': 'api1:pizza-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.Pizza.objects.all(),
                'required': False,
            },
            'extra': {
                'view_name': 'api1:extra-detail',
                'lookup_field': 'slug',
                'queryset': extras_models.Extra.objects.all(),
                'required': False,
            },
            'size': {
                'view_name': 'api1:size-detail',
                'lookup_field': 'metric',
                'queryset': pizza_models.Size.objects.all(),
                'required': False,
            },
            'crust': {
                'view_name': 'api1:crust-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.Crust.objects.all(),
                'required': False,
            },
        }

    def validate(self, attrs: dict) -> dict:
        """
        Check item compatibility.

        Components can be selected if and only if a pizza is also selected.
        Pizza cannot be selected together with an extra.
        It was simpler to place this here than in the child serializer or
        validators, unfortunately it doesn't looks nice :(
        """
        # Using these weird fallbacks ensures uniform validation for create and update
        pizza = attrs.get('pizza') or getattr(self.instance, 'pizza', None)

        if pizza:
            if attrs.get('extra'):
                raise serializers.ValidationError({'extra': [
                    'Cannot select pizza and extra together, add a separate item instead.',
                ]}, code='extra_and_pizza')
            crust = attrs.get('crust') or getattr(self.instance, 'crust', None)
            if not crust:
                raise serializers.ValidationError({'crust': [
                    'Crust must be selected for pizza.',
                ]}, code='crust_required')
            if crust not in pizza.available_crusts.all():
                raise serializers.ValidationError({'crust': [
                    'This crust is not available for this pizza.',
                ]}, code='invalid_crust')

            size = attrs.get('size') or getattr(self.instance, 'size', None)
            if not size:
                raise serializers.ValidationError({'size': [
                    'Size must be selected for pizza.',
                ]}, code='size_required')
            if size not in pizza.available_sizes.all():
                raise serializers.ValidationError({'size': [
                    'This size is not available for this pizza.',
                ]}, code='invalid_size')

        for component in attrs.get('components', []):
            if not pizza:
                raise serializers.ValidationError({'components': [{
                    'component': [
                        'Cannot select components without a pizza.',
                    ],
                }]}, code='pizza_required')
            if component['component'].pizza != pizza:
                raise serializers.ValidationError({'components': [{
                    'component': [
                        f'{component["component"].slug} cannot be selected with this pizza.',
                    ],
                }]}, code='invalid_component')
                # We can validate amounts here as well
        return attrs


class OrderSerializer(
        drf_writable_nested.mixins.NestedCreateMixin,
        drf_writable_nested.mixins.NestedUpdateMixin,
        serializers.HyperlinkedModelSerializer,
):
    items = OrderItemSerializer(
        many=True,
    )

    class Meta:
        model = orders_models.Order
        fields = ['uid', 'mid', 'address', 'notes', 'items']

    @classmethod
    def prefetch(cls, queryset: QuerySet) -> QuerySet:
        return (
            queryset
            .prefetch_related(
                # These three can be optimized further with Prefetch
                'items__pizza', 'items__crust', 'items__size',
                'items__components__component',
            )
        )
