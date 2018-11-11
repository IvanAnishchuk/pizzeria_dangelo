import pytest

import pizzeria_dangelo.customer_orders.tests.factories as orders_factories
import pizzeria_dangelo.extras.tests.factories as extras_factories
import pizzeria_dangelo.pizza.tests.factories as pizza_factories
from pizzeria_dangelo.pizza.tests.conftest import crust, size, pizza as another_pizza  # noqa F401


@pytest.fixture
def order():  # FIXME typing
    return orders_factories.OrderFactory()


@pytest.fixture
def pizza():
    # FIXME: This is redundant, solve the circular thingy somehow
    # Though right now it generates the same objects anyway
    return pizza_factories.PizzaFactory(
        name='Best pizza ever',
        slug='best-pizza-ever',
        components=['Cheese', 'Meat', 'Nicer cheese', 'Tomatoes', 'Sauce'],
        available_crusts=['Generic crust', 'Triple cheese sausage crust'],
        available_sizes=[50, 100, 150, 9000],
    )


@pytest.fixture
def drink(db):
    return extras_factories.ExtraFactory(
        name='Classic Coke (can)',
        slug='classic-coke-can',
    )


@pytest.fixture
def side(db):
    return extras_factories.ExtraFactory(
        name='Ultranice finest fresh herbs',
        slug='ultranice-finest-fresh-herbs',
    )
