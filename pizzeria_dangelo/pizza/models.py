from django.db import models

import utils.models


class Crust(utils.models.SlugMixin, utils.models.IDModel):
    """
    Crust type: pan, thin, etc.
    """
    namespace_id = 10
    pattern_name_api1 = 'crust-detail'
    description = models.TextField(
        blank=True,
    )


class Topping(utils.models.SlugMixin, utils.models.IDModel):
    """
    Topping: cheese, meat, veggies, etc.
    """
    namespace_id = 11
    pattern_name_api1 = 'topping-detail'
    description = models.TextField(
        blank=True,
    )


class Size(utils.models.IDModel):
    """
    Size, in CM.
    """
    namespace_id = 12
    pattern_name_api1 = 'size-detail'
    lookup_field = 'metric'
    metric = models.IntegerField(  # A slug could work better, depending
        help_text="Pizza size in CM",
        unique=True,
    )
    # But with this we could use several size units adding fields here
    # and never rely on autoconversion... With slugs, on the other hand,
    # we could use custom names for sizes, like "large" or "xlarge".


class Pizza(utils.models.SlugMixin, utils.models.IDModel):
    """
    Pizza type: margherita, marinara, etc.

    Prices and totals calculations are skipped for simplicity here,
    we assume that someone receives an order and adds everything up
    manually and cash is paid on delivery (business as usual in many
    pizza shops).
    """
    namespace_id = 13
    pattern_name_api1 = 'pizza-detail'
    description = models.TextField(
        blank=True,
    )
    # Available components use an explicit model below
    available_crusts = models.ManyToManyField(
        Crust,
        blank=True,
    )
    available_sizes = models.ManyToManyField(
        Size,
        blank=True,
    )


class PizzaComponent(utils.models.IDModel):
    """
    M2M relation model between pizza and topping.

    How many units of the topping is in the pizza by default.
    """
    namespace_id = 14  # maybe better lowercase this?
    pattern_name_api1 = 'pizzacomponent-detail'
    lookup_field = 'slug'
    # NOTE: not using slug mixin because we don't have name here
    slug = models.SlugField(  # consider adding automagic default
        # (probably in pre_save)
        max_length=128,
        unique=True,
    )
    pizza = models.ForeignKey(
        Pizza,
        related_name='components',
        on_delete=models.CASCADE,
    )
    topping = models.ForeignKey(
        Topping,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        default=0,
    )

    class Meta:
        unique_together = [
            ('pizza', 'topping'),
        ]
