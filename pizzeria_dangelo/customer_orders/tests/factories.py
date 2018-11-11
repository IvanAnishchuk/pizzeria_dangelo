import random  # random.choice is usually unsafe but ok for tests
import typing

import factory

import pizzeria_dangelo.customer_orders.models
import pizzeria_dangelo.extras.tests.factories
import pizzeria_dangelo.pizza.tests.factories


class PizzaFactory(factory.DjangoModelFactory):
    pizza = factory.SubFactory(
        pizzeria_dangelo.pizza.tests.factories.PizzaFactory,
        name='Best pizza ever',
        slug='best_pizza_ever',
        components=['Cheese', 'Meat', 'Nicer cheese', 'Tomatoes', 'Sauce'],
        available_crusts=['Generic crust', 'Triple cheese sausage crust'],
        available_sizes=[50, 100, 150, 9000],
    )
    crust = factory.LazyAttribute(
        lambda o: random.choice(  # nosec
            o.pizza
            .available_crusts
            .all() or [None],
        ),
    )
    size = factory.LazyAttribute(
        lambda o: random.choice(  # nosec
            o.pizza
            .available_sizes
            .all() or [None],
        ),
    )
    amount = 1

    @factory.post_generation
    def components(
        self,
        create: bool,
        extracted: typing.Sequence[typing.Union[pizzeria_dangelo.pizza.models.PizzaComponent, str]],
        **kwargs: typing.Any,
    ) -> None:

        if not create:
            return

        if extracted:
            for component in extracted:
                if not isinstance(component, pizzeria_dangelo.pizza.models.PizzaComponent):
                    raise ValueError('Must be a list of PizzaComponent objects')
                self.components.get_or_create(
                    item=self,
                    component=component,
                    defaults={'amount': 1},
                )
        else:
            for component in self.pizza.components.all():
                self.components.get_or_create(
                    item=self,
                    component=component,
                    defaults={'amount': 1},
                )
        self.refresh_from_db()

    class Meta:
        model = pizzeria_dangelo.customer_orders.models.OrderItem


class ExtraFactory(factory.DjangoModelFactory):
    extra = factory.SubFactory(pizzeria_dangelo.extras.tests.factories.ExtraFactory)
    amount = 1

    class Meta:
        model = pizzeria_dangelo.customer_orders.models.OrderItem


class OrderFactory(factory.DjangoModelFactory):

    address = factory.Sequence(lambda n: "Address {0}".format(n))
    # order items as related factories
    extra = factory.RelatedFactory(ExtraFactory, 'order')
    pizza = factory.RelatedFactory(PizzaFactory, 'order')

    class Meta:
        model = pizzeria_dangelo.customer_orders.models.Order
