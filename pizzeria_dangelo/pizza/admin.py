from django.contrib import admin

import pizzeria_dangelo.pizza.models


class ComponentInline(admin.TabularInline):
    model = pizzeria_dangelo.pizza.models.PizzaComponent


@admin.register(pizzeria_dangelo.pizza.models.Pizza)
class PizzaAdmin(admin.ModelAdmin):
    inlines = [
        ComponentInline,
    ]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(pizzeria_dangelo.pizza.models.Topping)
class ToppingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}


@admin.register(pizzeria_dangelo.pizza.models.Crust)
class CrustAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}


admin.site.register(pizzeria_dangelo.pizza.models.PizzaComponent)
admin.site.register(pizzeria_dangelo.pizza.models.Size)
