"""
Tests CRUDing pizzas and options using api v1.

More than required for 100% coverage, this covers every possible method
for every endpoint in case we refactor or reconfigure anything in future.
Except PUT, I'm generally against PUT, I'd probably forbid using it without
If-Match, We even have nice mid fields for that but deciding how to implement
the logic is not currently a priority, maybe in base classes v2.0 or so...
There's an on-going discussion whether tests like this should be
generalized and parametrized. Having four test functions for every single
CRUD endpoint does feel excessive at times but I think the overhead is
pretty low here so far and ability to add special cases is more important
at least given the current project structure. Maybe when we have, like,
hundreds of similarly-behaving models and endpoints the priorities will
shift somewhat.
"""
from django.urls import reverse
import pytest
from rest_framework.test import APIClient

import pizzeria_dangelo.pizza.models as pizza_models

pytestmark = pytest.mark.django_db


def test_post_pizza(
        client: APIClient,
        topping: pizza_models.Topping,
        size: pizza_models.Size,
        crust: pizza_models.Crust,
) -> None:
    resp = client.post(
        reverse('api1:pizza-list'),
        data={
            'name': 'Some pizza', 'slug': 'some_pizza',
            'available_crusts': [crust.get_url('api1')],
            'available_sizes': [size.get_url('api1')],
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        pizza_models.Pizza.objects
        .filter(slug='some_pizza')
        .exists()
    )


def test_get_pizza(client: APIClient, pizza: pizza_models.Pizza) -> None:
    resp = client.get(reverse('api1:pizza-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert pizza.slug in [item['slug'] for item in resp.data]

    resp = client.get(pizza.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert pizza.slug == resp.data['slug']


def test_patch_pizza(
        client: APIClient,
        pizza: pizza_models.Pizza,
        topping: pizza_models.Topping,
        size: pizza_models.Size,
        crust: pizza_models.Crust,
) -> None:
    resp = client.patch(
        pizza.get_url('api1'),
        data={
            'description': 'Lorem ipsum',
            'available_crusts': [
                pizza.available_crusts.all()[0].get_url('api1'),
                crust.get_url('api1'),
            ],
            'available_sizes': [
                pizza.available_sizes.all()[0].get_url('api1'),
                size.get_url('api1'),
            ],
            # Components have a separate endpoint
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    pizza.refresh_from_db()
    assert pizza.description == 'Lorem ipsum'
    assert size in pizza.available_sizes.all()
    assert crust in pizza.available_crusts.all()


def test_delete_pizza(client: APIClient, pizza: pizza_models.Pizza) -> None:
    resp = client.delete(pizza.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not pizza_models.Pizza.objects.filter(slug=pizza.slug).exists()


def test_post_crust(client: APIClient) -> None:
    resp = client.post(
        reverse('api1:crust-list'),
        data={
            'name': 'Some crust', 'slug': 'some_crust',
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        pizza_models.Crust.objects
        .filter(slug='some_crust')
        .exists()
    )


def test_get_crust(client: APIClient, crust: pizza_models.Crust) -> None:
    resp = client.get(reverse('api1:crust-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert crust.slug in [item['slug'] for item in resp.data]

    resp = client.get(crust.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert crust.slug == resp.data['slug']


def test_patch_crust(client: APIClient, crust: pizza_models.Crust) -> None:
    resp = client.patch(
        crust.get_url('api1'),
        data={
            'name': 'Lorem ipsum',
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    crust.refresh_from_db()
    assert crust.name == 'Lorem ipsum'


def test_delete_crust(client: APIClient, crust: pizza_models.Crust) -> None:
    resp = client.delete(crust.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not pizza_models.Crust.objects.filter(slug=crust.slug).exists()


def test_post_size(client: APIClient) -> None:
    resp = client.post(
        reverse('api1:size-list'),
        data={
            'metric': 111,
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        pizza_models.Size.objects
        .filter(metric=111)
        .exists()
    )


def test_get_size(client: APIClient, size: pizza_models.Size) -> None:
    resp = client.get(reverse('api1:size-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert size.metric in [item['metric'] for item in resp.data]

    resp = client.get(size.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert size.metric == resp.data['metric']


def test_patch_size(client: APIClient, size: pizza_models.Size) -> None:
    # FIXME: I'm not sure whether size should be updatable at all
    resp = client.patch(
        size.get_url('api1'),
        data={
            'metric': 123,
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    size.refresh_from_db()
    assert size.metric == 123


def test_delete_size(client: APIClient, size: pizza_models.Size) -> None:
    resp = client.delete(size.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not pizza_models.Size.objects.filter(metric=size.metric).exists()


def test_post_topping(client: APIClient) -> None:
    resp = client.post(
        reverse('api1:topping-list'),
        data={
            'name': 'Some topping', 'slug': 'some_topping',
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        pizza_models.Topping.objects
        .filter(slug='some_topping')
        .exists()
    )


def test_get_topping(client: APIClient, topping: pizza_models.Topping) -> None:
    resp = client.get(reverse('api1:topping-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert topping.slug in [item['slug'] for item in resp.data]

    resp = client.get(topping.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert topping.slug == resp.data['slug']


def test_patch_topping(client: APIClient, topping: pizza_models.Topping) -> None:
    resp = client.patch(
        topping.get_url('api1'),
        data={
            'name': 'Lorem ipsum',
            'description': 'Lorem ipsum',
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    topping.refresh_from_db()
    assert topping.name == 'Lorem ipsum'
    assert topping.description == 'Lorem ipsum'


def test_delete_topping(client: APIClient, topping: pizza_models.Topping) -> None:
    resp = client.delete(topping.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not pizza_models.Topping.objects.filter(slug=topping.slug).exists()


def test_post_pizzacomponent(
        client: APIClient,
        pizza: pizza_models.Pizza,
        topping: pizza_models.Topping,
) -> None:
    resp = client.post(
        reverse('api1:pizzacomponent-list'),
        data={
            'slug': f'{topping.slug}_in_{pizza.slug}',
            'pizza': pizza.get_url('api1'),
            'topping': topping.get_url('api1'),
            'amount': 1,
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    assert (
        pizza_models.PizzaComponent.objects
        .filter(
            slug=f'{topping.slug}_in_{pizza.slug}',
            pizza=pizza,
            topping=topping,
            amount=1,
        )
        .exists()
    )


def test_get_pizzacomponent(client: APIClient, pizza: pizza_models.Pizza) -> None:
    component = pizza.components.all()[0]
    resp = client.get(reverse('api1:pizzacomponent-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert component.slug in [item['slug'] for item in resp.data]

    resp = client.get(component.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert component.slug == resp.data['slug']


def test_patch_pizzacomponent(client: APIClient, pizza: pizza_models.Pizza) -> None:
    component = pizza.components.all()[0]
    resp = client.patch(
        component.get_url('api1'),
        data={
            'amount': 5,
        },
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    component.refresh_from_db()
    assert component.amount == 5


def test_delete_pizzacomponent(client: APIClient, pizza: pizza_models.Pizza) -> None:
    component = pizza.components.all()[0]
    resp = client.delete(component.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not pizza_models.PizzaComponent.objects.filter(slug=component.slug).exists()
