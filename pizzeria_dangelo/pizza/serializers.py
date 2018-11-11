from django.db.models.query import QuerySet
from rest_framework import serializers

import pizzeria_dangelo.pizza.models as pizza_models


class PizzaSizeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pizza_models.Size
        fields = ['uid', 'mid', 'metric']


class PizzaCrustSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pizza_models.Crust
        fields = ['uid', 'mid', 'slug', 'name', 'description']


class PizzaToppingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pizza_models.Topping
        fields = ['uid', 'mid', 'slug', 'name', 'description']
        extra_kwargs = {
            'description': {
                'required': False,
            },
        }


class PizzaComponentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pizza_models.PizzaComponent
        fields = ['uid', 'mid', 'slug', 'pizza', 'topping', 'amount']
        extra_kwargs = {
            'pizza': {
                'view_name': 'api1:pizza-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.Pizza.objects.all(),
            },
            'topping': {
                'view_name': 'api1:topping-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.Topping.objects.all(),
            },
        }


class PizzaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pizza_models.Pizza
        fields = [
            'uid', 'mid', 'name', 'slug', 'description',
            'available_sizes', 'available_crusts', 'components',
        ]
        extra_kwargs = {
            'description': {
                'required': False,
            },
            'available_sizes': {
                'view_name': 'api1:size-detail',
                'lookup_field': 'metric',
                'queryset': pizza_models.Size.objects.all(),
            },
            'available_crusts': {
                'view_name': 'api1:crust-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.Crust.objects.all(),
            },
            'components': {
                'view_name': 'api1:pizzacomponent-detail',
                'lookup_field': 'slug',
                'queryset': pizza_models.PizzaComponent.objects.all(),
            },
        }

    @classmethod
    def prefetch(cls, queryset: QuerySet) -> QuerySet:
        return (
            queryset
            .prefetch_related(
                'available_sizes', 'available_crusts',
                'components',
            )
        )
