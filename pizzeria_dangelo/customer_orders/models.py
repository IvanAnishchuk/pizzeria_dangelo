from django.db import models

import utils.models


class Order(utils.models.IDModel):
    """
    Customer order: some items should be delivered to the address.
    """
    namespace_id = 21
    pattern_name_api1 = 'order-detail'
    address = models.CharField(max_length=256)  # keeping it simple
    notes = models.TextField(
        blank=True,
    )


class OrderItem(utils.models.IDModel):
    """
    Order item: could be a pizza or an extra.

    This adds some polymorphism. Not much but hopefully just enough.
    """
    namespace_id = 22
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
    )
    pizza = models.ForeignKey(
        'pizza.Pizza',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    size = models.ForeignKey(
        'pizza.Size',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    crust = models.ForeignKey(
        'pizza.Crust',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    extra = models.ForeignKey(
        'extras.Extra',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text='Not to use together with pizza fields',
    )
    amount = models.IntegerField(
        default=1,
    )


class OrderComponent(utils.models.IDModel):
    """
    Order component, adjusts pizza component for a particular order.

    Amounts are additive: if a pizza has 2 units of olive oil in it and order
    sets -2 units for olive oil it means zero olive oil in this pizza for
    this order. I, however, omit all this calculations mainly because
    I don't have exact business requirements and can't decide which parts
    should be implemented in the backend and which in the clients.
    """
    namespace_id = 23
    item = models.ForeignKey(
        OrderItem,
        related_name='components',
        on_delete=models.CASCADE,
    )
    component = models.ForeignKey(
        'pizza.PizzaComponent',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        default=0,
    )

    class Meta:
        unique_together = [
            ('item', 'component'),
        ]
