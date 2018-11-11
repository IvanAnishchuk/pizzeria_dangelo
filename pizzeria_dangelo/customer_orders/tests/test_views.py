"""
Tests for orders api v1.

The main tests in this project so far covering the most complicated api
endpoint, with nested resources and everything.
"""
from django.urls import reverse
import pytest
from rest_framework.test import APIClient

import pizzeria_dangelo.customer_orders.models as orders_models
import pizzeria_dangelo.pizza.models as pizza_models
import pizzeria_dangelo.extras.models as extras_models

pytestmark = pytest.mark.django_db


def test_post_order(
        client: APIClient,
        pizza: pizza_models.Pizza,
        side: extras_models.Extra,
        drink: extras_models.Extra,
) -> None:
    data = {
        'address': '123 Main street, USA',
        'items': [
            {
                'pizza': pizza.get_url('api1'),
                'crust': pizza.available_crusts.last().get_url('api1'),
                'size': pizza.available_sizes.first().get_url('api1'),
                'components': [
                    {  # double helping of this, please
                        'component': pizza.components.first().get_url('api1'),
                        'amount': 2,
                    },
                    {  # none of those on my pie!
                        'component': pizza.components.last().get_url('api1'),
                        'amount': -1,
                    },
                ],
            },
            {
                'extra': side.get_url('api1'),
            },
        ],
    }
    resp = client.post(
        reverse('api1:order-list'),
        data=data,
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 201
    uid = resp.data['uid']
    assert (
        orders_models.Order.objects
        .filter(uid=uid)
        .exists()
    )


def test_get_order(client: APIClient, order: orders_models.Order) -> None:
    resp = client.get(reverse('api1:order-list'))
    print(resp.data)
    assert resp.status_code == 200
    assert str(order.uid) in [item['uid'] for item in resp.data]

    resp = client.get(order.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 200
    assert str(order.uid) == resp.data['uid']


def test_patch_order(
        client: APIClient,
        order: orders_models.Order,
        pizza: pizza_models.Pizza,
        side: extras_models.Extra,
        drink: extras_models.Extra,
) -> None:
    pizza_item = order.items.all().get(pizza__isnull=False)
    assert pizza_item.components.all().count() > 2
    extra_item = order.items.all().filter(extra__isnull=False).first()
    data = {
        'address': 'Elsewhere, somewhere, whatever',
        'notes': 'Lorem ipsum',
        'items': [
            # Generally we expect a copy of the original order list here
            # with values adjusted. It's not quite validated and
            # things can happen and something is missing or misplaced.
            # (E.g. something can be silently deleted or set to default.)
            # Validating it properly requires understanding of business
            # requirements, like which items can be amended and which are
            # already baking, which parts of original order to keep, etc.
            # and I have no business to survey for this.
            {
                'uid': pizza_item.uid,
                'pizza': pizza.get_url('api1'),
                'crust': pizza.available_crusts.last().get_url('api1'),
                'size': pizza.available_sizes.first().get_url('api1'),
                'components': [
                    {
                        'uid': pizza_item.components.all()[0].uid,
                        'component': pizza.components.first().get_url('api1'),
                        'amount': -1,
                    },
                    {
                        'uid': pizza_item.components.all()[1].uid,
                        'component': pizza.components.last().get_url('api1'),
                        'amount': 1,
                    },
                ],
            },
            {
                # This is an attempt to disambiguate the items,
                # it's not validated anywhere but maybe we should always
                # require ids for list patching?
                'uid': extra_item.uid,
                'extra': side.get_url('api1'),
                'amount': 5,
            },
            {
                'extra': drink.get_url('api1'),
                'amount': 2,
            },
        ],
    }
    resp = client.patch(
        order.get_url('api1'),
        data=data,
        format='json',
    )
    print(resp.data)
    assert resp.status_code == 200
    order.refresh_from_db()
    pizza_item.refresh_from_db()  # we can confirm the objects were updated
    extra_item.refresh_from_db()  # in-place and not re-created or something
    assert order.notes == 'Lorem ipsum'
    assert pizza_item.components.all().count() == 2
    assert pizza_item.pizza == pizza
    assert pizza_item.crust == pizza.available_crusts.last()
    assert pizza_item.size == pizza.available_sizes.first()
    assert extra_item.amount == 5
    assert order.items.all()[2].amount == 2


def test_delete_order(client: APIClient, order: orders_models.Order) -> None:
    resp = client.delete(order.get_url('api1'))
    print(resp.data)
    assert resp.status_code == 204
    assert not orders_models.Order.objects.filter(uid=order.uid).exists()
