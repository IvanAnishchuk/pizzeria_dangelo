from django.db import models


import utils.models


class Extra(utils.models.SlugMixin, utils.models.IDModel):
    """
    Things for sale that are not pizza.

    Anything from drinks and sauces to dipping sticks and salads.
    """
    namespace_id = 31
    pattern_name_api1 = 'extra-detail'
    description = models.TextField(
        blank=True,
    )
    category = models.ForeignKey(
        'extras.ExtraCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )


class ExtraCategory(utils.models.SlugMixin, utils.models.IDModel):
    """
    Basically menu pages for the site and mobile apps.
    """
    namespace_id = 32
    pattern_name_api1 = 'extracategory-detail'
    description = models.TextField(
        blank=True,
    )
