"""
Basic coverage of pizza models code.

As the models don't have much custom code yet, this thoroughly covers both
methods they actually define at this moment (one could probably generate this).
"""
import pytest
from django.core.exceptions import ImproperlyConfigured

import pizzeria_dangelo.pizza.models as pizza_models

pytestmark = pytest.mark.django_db


def test_pizza_str(pizza: pizza_models.Pizza) -> None:
    assert str(pizza) == f'pizza: {pizza.slug}'


def test_crust_str(crust: pizza_models.Crust) -> None:
    assert str(crust) == f'crust: {crust.slug}'


def test_size_str(size: pizza_models.Size) -> None:
    assert str(size) == f'size: {size.metric}'


def test_topping_str(topping: pizza_models.Topping) -> None:
    assert str(topping) == f'topping: {topping.slug}'


def test_pizzacomponent_str(pizza: pizza_models.Pizza) -> None:
    component = pizza.components.all()[0]
    assert str(component) == f'pizzacomponent: {component.slug}'


def test_pizza_get_url(pizza: pizza_models.Pizza) -> None:
    assert pizza.get_url('api1') == f'/api/1/pizzas/{pizza.slug}/'
    with pytest.raises(ImproperlyConfigured):
        pizza.get_url('api999')


def test_crust_get_url(crust: pizza_models.Crust) -> None:
    assert crust.get_url('api1') == f'/api/1/crusts/{crust.slug}/'
    with pytest.raises(ImproperlyConfigured):
        crust.get_url('api999')


def test_size_get_url(size: pizza_models.Size) -> None:
    assert size.get_url('api1') == f'/api/1/sizes/{size.metric}/'
    with pytest.raises(ImproperlyConfigured):
        size.get_url('api999')


def test_pizzacomponent_get_url(pizza: pizza_models.Pizza) -> None:
    component = pizza.components.all()[0]
    assert component.get_url('api1') == f'/api/1/pizzacomponents/{component.slug}/'
    with pytest.raises(ImproperlyConfigured):
        component.get_url('api999')


def test_topping_get_url(topping: pizza_models.Topping) -> None:
    assert topping.get_url('api1') == f'/api/1/toppings/{topping.slug}/'
    with pytest.raises(ImproperlyConfigured):
        topping.get_url('api999')
