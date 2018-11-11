import pytest

import pizzeria_dangelo.pizza.tests.factories as pizza_factories


@pytest.fixture
def crust(db):
    return pizza_factories.CrustFactory()


@pytest.fixture
def size(db):
    return pizza_factories.SizeFactory()


@pytest.fixture
def topping(db):
    return pizza_factories.ToppingFactory()


@pytest.fixture
def pizza(db):
    # NOTE: different options from above
    return pizza_factories.PizzaFactory(
        available_crusts=[pizza_factories.CrustFactory()],
        available_sizes=[pizza_factories.SizeFactory()],
        components=[pizza_factories.ToppingFactory()],
    )
