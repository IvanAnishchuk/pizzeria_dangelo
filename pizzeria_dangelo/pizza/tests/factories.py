import typing

import factory
from slugify import slugify

import pizzeria_dangelo.pizza.models


class CrustFactory(factory.DjangoModelFactory):

    name = factory.Sequence(lambda n: "Crust {0}".format(n))
    slug = factory.Sequence(lambda n: "crust_{0}".format(n))

    class Meta:
        model = pizzeria_dangelo.pizza.models.Crust
        django_get_or_create = ["slug"]


class SizeFactory(factory.DjangoModelFactory):

    metric = factory.Sequence(lambda n: n)

    class Meta:
        model = pizzeria_dangelo.pizza.models.Size
        django_get_or_create = ["metric"]


class ToppingFactory(factory.DjangoModelFactory):

    name = factory.Sequence(lambda n: "Topping {0}".format(n))
    slug = factory.Sequence(lambda n: "topping_{0}".format(n))

    class Meta:
        model = pizzeria_dangelo.pizza.models.Topping
        django_get_or_create = ["slug"]


class PizzaFactory(factory.DjangoModelFactory):

    name = factory.Sequence(lambda n: "Pizza {0}".format(n))
    slug = factory.Sequence(lambda n: "pizza_{0}".format(n))

    @factory.post_generation
    def available_crusts(
            self,
            create: bool,
            extracted: typing.Sequence[typing.Union[pizzeria_dangelo.pizza.models.Crust, str]],
            **kwargs: typing.Any,
    ) -> None:
        if not create:
            return

        if extracted:
            for crust in extracted:
                if isinstance(crust, str):
                    instance, _ = (
                        pizzeria_dangelo.pizza.models.Crust
                        .objects
                        .get_or_create(
                            slug=slugify(crust),
                            defaults={'name': crust},
                        )
                    )
                elif isinstance(crust, pizzeria_dangelo.pizza.models.Crust):
                    instance = crust
                else:
                    raise ValueError('Must be a list of str or Crust objects')
                self.available_crusts.add(instance)

    @factory.post_generation
    def available_sizes(
            self, create: bool,
            extracted: typing.Sequence[typing.Union[pizzeria_dangelo.pizza.models.Size, int]],
            **kwargs: typing.Any,
    ) -> None:
        if not create:
            return

        if extracted:
            for size in extracted:
                if isinstance(size, int):
                    instance, _ = (
                        pizzeria_dangelo.pizza.models.Size
                        .objects
                        .get_or_create(metric=size)
                    )
                elif isinstance(size, pizzeria_dangelo.pizza.models.Size):
                    instance = size
                else:
                    raise ValueError('Must be a list of int or Size objects')
                self.available_sizes.add(instance)

    @factory.post_generation
    def components(
        self,
        create: bool,
        extracted: typing.Sequence[typing.Union[pizzeria_dangelo.pizza.models.Topping, str]],
        **kwargs: typing.Any,
    ) -> None:
        if not create:
            return

        if extracted:
            for topping in extracted:
                if isinstance(topping, str):
                    instance, _ = (
                        pizzeria_dangelo.pizza.models.Topping
                        .objects
                        .get_or_create(
                            slug=slugify(topping),
                            defaults={'name': topping},
                        )
                    )
                elif isinstance(topping, pizzeria_dangelo.pizza.models.Topping):
                    instance = topping
                else:
                    raise ValueError('Must be a list of str or Topping objects')
                self.components.create(
                    slug=f'{instance.slug}_in_{self.slug}',
                    topping=instance,
                    amount=1,  # XXX: Hmmm... what if we specify toppings twice meaning amount=2 and so on?...
                )

    class Meta:
        model = pizzeria_dangelo.pizza.models.Pizza
        django_get_or_create = ["slug"]
