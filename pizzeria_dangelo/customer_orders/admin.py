from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

import pizzeria_dangelo.customer_orders.models


class ItemInline(admin.TabularInline):
    model = pizzeria_dangelo.customer_orders.models.OrderItem

    def get_url(  # pylint: disable=no-self-use
            self,
            instance: pizzeria_dangelo.customer_orders.models.OrderItem,
    ) -> str:
        url = reverse(
            f'admin:{instance._meta.app_label}_{instance._meta.model_name}_change',
            args=[instance.uid],
        )
        # No user-supplied data used -> mostly safe, disabling the bandit warning
        # (but, still, be careful with changes here)
        return mark_safe(f'<a href="{url}">{instance}</a>')  # nosec

    get_url.allow_tags = True  # noqa
    get_url.short_description = "Details"  # noqa

    readonly_fields = [
        'get_url',
    ]


@admin.register(pizzeria_dangelo.customer_orders.models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ItemInline,
    ]


class ComponentInline(admin.TabularInline):
    model = pizzeria_dangelo.customer_orders.models.OrderComponent


@admin.register(pizzeria_dangelo.customer_orders.models.OrderItem)
class ItemAdmin(admin.ModelAdmin):
    inlines = [
        ComponentInline,
    ]


admin.site.register(pizzeria_dangelo.customer_orders.models.OrderComponent)
