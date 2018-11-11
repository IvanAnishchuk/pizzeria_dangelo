from django.db.models.query import QuerySet
from rest_framework import serializers

import pizzeria_dangelo.extras.models as extras_models


class ExtraSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = extras_models.Extra
        fields = ['uid', 'mid', 'slug', 'name', 'category', 'description']
        extra_kwargs = {
            'category': {
                'view_name': 'api1:extracategory-detail',
                'lookup_field': 'slug',
                'queryset': extras_models.ExtraCategory.objects.all(),
            },
            'description': {
                'required': False,
            },
        }

    @classmethod
    def prefetch(cls, queryset: QuerySet) -> QuerySet:
        return (
            queryset
            .prefetch_related(
                'category',
            )
        )


class ExtraCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = extras_models.ExtraCategory
        fields = ['uid', 'mid', 'slug', 'name', 'description']
        extra_kwargs = {
            'description': {
                'required': False,
            },
        }
