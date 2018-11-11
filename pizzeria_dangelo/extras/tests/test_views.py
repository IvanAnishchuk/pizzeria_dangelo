from django.urls import reverse
import pytest
from rest_framework.test import APIClient

import pizzeria_dangelo.extras.models as extras_models

pytestmark = pytest.mark.django_db


def test_post_extra(
        client: APIClient,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.post(
        reverse('api1:extra-list'),
        data={
            'name': 'Some food', 'slug': 'some_food',
            'category': category.get_url('api1'),
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        extras_models.Extra.objects
        .filter(slug='some_food', category=category)
        .exists()
    )


def test_get_extra(client: APIClient, extra: extras_models.Extra) -> None:
    resp = client.get(reverse('api1:extra-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert extra.slug in [item['slug'] for item in resp.data]

    resp = client.get(extra.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert extra.slug == resp.data['slug']


def test_patch_extra(
        client: APIClient,
        extra: extras_models.Extra,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.patch(
        extra.get_url('api1'),
        data={
            'description': 'Lorem ipsum',
            'category': category.get_url('api1'),
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    extra.refresh_from_db()
    assert extra.description == 'Lorem ipsum'
    assert extra.category == category


def test_delete_extra(client: APIClient, extra: extras_models.Extra) -> None:
    resp = client.delete(extra.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not extras_models.Extra.objects.filter(slug=extra.slug).exists()


def test_post_category(
        client: APIClient,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.post(
        reverse('api1:extracategory-list'),
        data={'name': 'Another category', 'slug': 'another_category'},
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        extras_models.ExtraCategory.objects
        .filter(slug='another_category')
        .exists()
    )


def test_get_category(
        client: APIClient,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.get(reverse('api1:extracategory-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert category.slug in [item['slug'] for item in resp.data]

    resp = client.get(category.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert category.slug == resp.data['slug']


def test_patch_category(
        client: APIClient,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.patch(
        category.get_url('api1'),
        data={'description': 'Lorem ipsum'},
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    category.refresh_from_db()
    assert category.description == 'Lorem ipsum'


def test_delete_category(
        client: APIClient,
        category: extras_models.ExtraCategory,
) -> None:
    resp = client.delete(category.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not (
        extras_models.ExtraCategory.objects
        .filter(slug=category.slug)
        .exists()
    )
