"""
A couple additional tests for order serializers.

Mainly covering custom validation. Add new tests when we have more of that.
"""
import collections
from rest_framework.test import APIClient
import pytest

import pizzeria_dangelo.customer_orders.models as orders_models
import pizzeria_dangelo.customer_orders.serializers as orders_serializers
import pizzeria_dangelo.extras.models as extras_models
import pizzeria_dangelo.pizza.models as pizza_models

pytestmark = pytest.mark.django_db
# We essentially only need this to pass method
# (use a proper generator if the needs change)
FakeRequest = collections.namedtuple('Request', ['method'])


def test_order_item_validation(
        client: APIClient,
        order: orders_models.Order,
        pizza: pizza_models.Pizza,
        drink: extras_models.Extra,
        crust: pizza_models.Crust,
        size: pizza_models.Size,
        another_pizza: pizza_models.Pizza,
) -> None:
    """
    Thoroughly try every invalid field combination and check the coded.

    This can be parametrized with a data fixture or something.
    """
    serializer = orders_serializers.OrderItemSerializer(
        data={
            'pizza': pizza.get_url('api1'),
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'crust' in serializer.errors
    assert serializer.errors['crust'][0].code == 'crust_required'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'pizza': pizza.get_url('api1'),
            'crust': crust.get_url('api1'),  # incompatible
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'crust' in serializer.errors
    assert serializer.errors['crust'][0].code == 'invalid_crust'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'pizza': pizza.get_url('api1'),
            'crust': pizza.available_crusts.all()[0].get_url('api1'),
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'size' in serializer.errors
    assert serializer.errors['size'][0].code == 'size_required'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'pizza': pizza.get_url('api1'),
            'crust': pizza.available_crusts.all()[0].get_url('api1'),
            'size': size.get_url('api1'),
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'size' in serializer.errors
    assert serializer.errors['size'][0].code == 'invalid_size'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'pizza': pizza.get_url('api1'),
            'crust': pizza.available_crusts.all()[0].get_url('api1'),
            'size': pizza.available_sizes.all()[0].get_url('api1'),
            'components': [
                {
                    'component': another_pizza.components.all()[0].get_url('api1'),
                },
            ],
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'components' in serializer.errors
    assert serializer.errors['components'][0]['component'][0].code == 'invalid_component'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'components': [
                {
                    'component': another_pizza.components.all()[0].get_url('api1'),
                },
            ],
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'components' in serializer.errors
    assert serializer.errors['components'][0]['component'][0].code == 'pizza_required'

    serializer = orders_serializers.OrderItemSerializer(
        data={
            'extra': drink.get_url('api1'),
            'pizza': pizza.get_url('api1'),
        },
        context={
            'request': FakeRequest('POST'),
            'view': None,
        },
    )
    assert not serializer.is_valid()
    assert 'extra' in serializer.errors
    assert serializer.errors['extra'][0].code == 'extra_and_pizza'
