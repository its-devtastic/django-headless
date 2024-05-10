from decimal import Decimal

from django.db import models
from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend

from headless.registry import registry
from headless.utils import flatten


class FilterBackend(BaseFilterBackend):
    """
    A permissive filter backend that basically allows every supported lookup
    for a given field. Only works on models that are in the content type registry.
    Only fields that are exposed by the content type (included in the "fields" property)
    are filterable. Automatically handles multi-value lookups.
    """

    MULTI_VALUE_LOOKUPS = ["in", "range"]

    EXCLUDE_SYMBOL = "~"

    NON_FILTER_FIELDS = [
        "search",
        "limit",
        "page",
        "fields",
        "exclude",
        "expand",
        "relation",
    ]

    def filter_queryset(self, request, queryset, view):
        # Only list views part of the generated REST routes are supported.
        # Use another backend, such as django-filter, for your own custom views.
        if getattr(view, "action", None) == "list" and hasattr(view, "resource_id"):
            try:
                filter_kwargs, exclude_kwargs = self.get_filter_kwargs(
                    content_type=registry.get(view.resource_id),
                    query_params=request.query_params,
                )
            except Exception as e:
                print(e)
                raise ParseError(detail="Invalid filter parameters")
            return queryset.filter(**filter_kwargs).exclude(**exclude_kwargs)

        return queryset

    def get_filter_kwargs(self, content_type, query_params):
        filter_kwargs = {}
        exclude_kwargs = {}

        allowed_fields = content_type.get_fields()
        field_lookups = self.get_field_lookups(model=content_type.model)

        for key, value in query_params.lists():
            if key in self.NON_FILTER_FIELDS:
                continue
            # By default Django supports repeated multi-values (e.g. `a=1&a=2`)
            # but we allow for comma-seperated multi-values as well (e.g. `a=1,2`).
            value = flatten([param.split(",") for param in value])
            is_exclude = key.startswith(self.EXCLUDE_SYMBOL)
            # The first part of a key is considered the field name
            field_name = key.split("__")[0]
            # Get the model field. If it's not in the allowed list we ignore it.
            try:
                field = next((f for f in allowed_fields if f.name == field_name))
            except StopIteration:
                continue
            # Get the allowed lookups for this field.
            lookups = field_lookups.get(field_name, [])
            try:
                # The last part of a key is considered its lookup
                # but it's not required.
                lookup = key.split("__")[-1]
                if lookup not in lookups:
                    lookup = None
            except IndexError:
                lookup = None

            # Some lookups allow multiple values, otherwise
            # the first value is used.
            is_multi = lookup in self.MULTI_VALUE_LOOKUPS
            # Depending on the field type we cast the value to
            # its correct type (i.e. number, boolean, etc.).
            if is_multi:
                casted_value = [self.cast_field_value(v, field) for v in value]
            elif lookup == "isnull":
                casted_value = value[0] in ["1", "true", "on"]
            else:
                casted_value = self.cast_field_value(value[0], field)

            if is_exclude:
                exclude_kwargs[key] = casted_value
            else:
                filter_kwargs[key] = casted_value

        return filter_kwargs, exclude_kwargs

    @staticmethod
    def get_field_lookups(model):
        """
        Allow all supported lookups.
        """
        field_lookups = {}
        for model_field in model._meta.get_fields():
            lookup_list = model_field.get_lookups().keys()
            field_lookups[model_field.name] = lookup_list
        return field_lookups

    def cast_field_value(self, value: str, field):
        value = value.strip().lower()

        if isinstance(field, models.BooleanField):
            if value in ["1", "true", "on"]:
                return True
            if value in ["0", "false", "off"]:
                return False
        if isinstance(field, models.NullBooleanField):
            if value in ["null", "none", "empty"]:
                return None

        if isinstance(field, models.IntegerField):
            return int(value)

        if isinstance(field, models.DecimalField):
            return Decimal(value)

        if isinstance(field, models.FloatField):
            return float(value)

        return value
