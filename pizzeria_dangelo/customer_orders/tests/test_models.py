"""
Tests covering order models code.

Just the basics, there's not much custom code there.
"""
import pytest
from django.core.exceptions import ImproperlyConfigured

import pizzeria_dangelo.customer_orders.models as order_models

pytestmark = pytest.mark.django_db


def test_order_str(order: order_models.Order) -> None:
    assert str(order) == f'order: {order.uid}'


def test_item_str(order: order_models.Order) -> None:
    assert order.items.exists()
    for item in order.items.all():
        assert str(item) == f'orderitem: {item.uid}'


def test_component_str(order: order_models.Order) -> None:
    assert order.items.exists()
    for item in order.items.all():
        print(item.uid, item.pizza, item.extra, item.components.all())
        if item.components.exists():
            for component in item.components.all():
                assert str(component) == f'ordercomponent: {component.uid}'
            break
    else:
        assert False, "No components found, fix the fixtures"


def test_order_get_url(order: order_models.Order) -> None:
    assert order.get_url('api1') == f'/api/1/orders/{order.uid}/'
    with pytest.raises(ImproperlyConfigured):
        order.get_url('api999')
