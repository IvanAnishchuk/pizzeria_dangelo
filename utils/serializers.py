import drf_writable_nested.mixins

from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


class UniqueFieldsMixin(drf_writable_nested.mixins.UniqueFieldsMixin):
    """
    Slightly customized copy-paste from drf_writable_nested

    Validation fix for missing values. The bug should probably be reported
    to upstream (after investigation).
    """
    def _validate_unique_fields(self, validated_data: dict) -> None:
        for field_name in self._unique_fields:
            unique_validator = UniqueValidator(self.Meta.model.objects.all())
            unique_validator.set_context(self.fields[field_name])
            if field_name in validated_data or not self.partial:
                # Skip for partial updates when data is missing
                # (if the field is required another error will pop)
                try:
                    unique_validator(validated_data[field_name])
                except ValidationError as exc:
                    raise ValidationError({field_name: exc.detail})
