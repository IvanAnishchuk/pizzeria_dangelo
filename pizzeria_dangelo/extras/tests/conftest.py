import pytest

import pizzeria_dangelo.extras.tests.factories as extras_factories


@pytest.fixture
def category(db):
    return extras_factories.CategoryFactory()


@pytest.fixture
def extra(db):
    # NOTE: not the same category
    return extras_factories.ExtraFactory()
