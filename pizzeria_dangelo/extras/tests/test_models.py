import pytest
from django.core.exceptions import ImproperlyConfigured

import pizzeria_dangelo.extras.models as extras_models

pytestmark = pytest.mark.django_db


def test_extra_str(extra: extras_models.Extra) -> None:
    """
    Exactly how it sounds: test __str__ method

    Covering __str__ methods is usually considered kinda low-priority
    but I had plenty of issues caused by them so I feel like they should
    at least be executed once.
    """
    assert str(extra) == f"extra: {extra.slug}"


def test_extra_get_url(extra: extras_models.Extra) -> None:
    assert extra.get_url('api1') == f"/api/1/extras/{extra.slug}/"
    with pytest.raises(ImproperlyConfigured):
        extra.get_url('api999')


def test_category_str(category: extras_models.ExtraCategory) -> None:
    assert str(category) == f"extracategory: {category.slug}"


def test_category_get_url(category: extras_models.ExtraCategory) -> None:
    assert category.get_url('api1') == f"/api/1/extracategories/{category.slug}/"
    with pytest.raises(ImproperlyConfigured):
        category.get_url('api999')
