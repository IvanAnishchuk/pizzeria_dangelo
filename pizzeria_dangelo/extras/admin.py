from django.contrib import admin

import pizzeria_dangelo.extras.models


@admin.register(pizzeria_dangelo.extras.models.Extra)
class ExtraAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}


@admin.register(pizzeria_dangelo.extras.models.ExtraCategory)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}
