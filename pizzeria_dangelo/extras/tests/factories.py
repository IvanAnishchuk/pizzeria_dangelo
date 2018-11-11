import factory

import pizzeria_dangelo.extras.models


class CategoryFactory(factory.DjangoModelFactory):

    name = factory.Sequence(lambda n: "Category {0}".format(n))
    slug = factory.Sequence(lambda n: "category_{0}".format(n))

    class Meta:
        model = pizzeria_dangelo.extras.models.ExtraCategory
        django_get_or_create = ["slug"]


class ExtraFactory(factory.DjangoModelFactory):

    name = factory.Sequence(lambda n: "Food {0}".format(n))
    slug = factory.Sequence(lambda n: "food_{0}".format(n))
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = pizzeria_dangelo.extras.models.Extra
        django_get_or_create = ["slug"]
