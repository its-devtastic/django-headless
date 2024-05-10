from django.db.models import FileField
from rest_flex_fields.serializers import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.fields import SkipField

from headless.fields import MultipleChoiceField
from headless.registry import registry
from headless.utils import get_resource_id


###
# Serializer fields
###
class MultipleChoiceSerializerField(serializers.MultipleChoiceField):
    """
    Serializer field for the MultipleChoiceField model field.
    """

    def __init__(self, encoder=None, decoder=None, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        # We need to convert the set to a list to be JSON-serializable
        return list(super().to_internal_value(data))


class FileFieldSerializerField(serializers.FileField):
    """
    Serializer field for handling files.
    """

    def to_internal_value(self, data):
        # Skip files if they are sent as strings (for example as URLs).
        # We assume the field should be left as-is.
        if isinstance(data, str):
            raise SkipField()

        return super().to_internal_value(data)


###
# Serializer classes
###
class ContentSerializer(FlexFieldsModelSerializer):
    """
    The default serializer is based on the flex fields model serializer.
    As content types have a serializer we can use these to automatically
    populate the expandable fields.
    """

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )

        # Multiple choice fields are stored as a JSONField
        if type(model_field) is MultipleChoiceField:
            field_class = MultipleChoiceSerializerField

        if type(model_field) is FileField:
            field_class = FileFieldSerializerField

        return field_class, field_kwargs

    @property
    def _expandable_fields(self) -> dict:
        """
        Relations that are registered as content types are automatically
        included in the expandable fields.
        """
        model = hasattr(self, "Meta") and self.Meta.model

        if not model:
            raise Exception("Cannot find model of default serializer.")

        fields = model._meta.get_fields()

        expandable_fields = {}

        for field in fields:
            if field.is_relation:
                resource_id = get_resource_id(field.related_model)
                content_type = registry.get(resource_id)

                if content_type:
                    serializer_class = content_type.get_serializer_class()
                    is_many = field.many_to_many or field.one_to_many
                    name = field.name

                    if field.one_to_many:
                        name = field.related_name or f"{name}_set"

                    expandable_fields[name] = (
                        serializer_class,
                        {"many": is_many},
                    )

        return expandable_fields
