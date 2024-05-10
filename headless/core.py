from functools import cache
from typing import Type, Literal

from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.auth import get_user_model
from django.db import models
from django.forms.models import _get_foreign_key
from rest_framework import serializers
from rest_framework.utils import model_meta

from headless.rest.serializers import ContentSerializer
from headless.rest.viewsets import ContentViewSet
from .registry import registry
from .utils import get_resource_id, is_jsonable, camelize_list


class ContentType(object):
    """
    Content type base class.
    """

    # ID for referring to this content type. Also used
    # in the auto-generated REST URLs.
    resource_id: str = None
    # The Django model for this content type.
    model = None
    # Serializer class for serializing content in REST API responses.
    serializer_class = ContentSerializer
    # View set for generating REST endpoints.
    viewset_class = ContentViewSet
    # Override default filterset class.
    filterset_class = None
    # Override default permission classes.
    permission_classes = None
    # Fields to include in serialization. By default, all fields are
    # included, but you can restrict the fields for more control.
    # Keep in mind that fields not included here will also not be
    # available in the Django Headless Admin.
    fields: [str] | Literal["__all__"] = "__all__"
    # Fields to exclude from serialization. Unlike in DRF you can define both
    # the `fields` and the `exclude` fields. The latter takes precedence.
    exclude: [str] = None
    # Fields to include in the search filter. By default, all fields defined above
    # are searchable. You can add more restriction or allow all fields regardless
    # of the `fields` setting. Note that only supported fields, such as char and
    # text fields are taken into account.
    search_fields: [str] | Literal["__all__"] | Literal["__fields__"] = "__fields__"

    def __init__(self, resource_id=None):
        self.resource_id = resource_id or get_resource_id(self.model)

        self.model._meta.resource_id = self.resource_id

    @property
    def model_name(self):
        return self.model and self.model._meta.model_name

    @property
    def is_singleton(self):
        return getattr(self.model, "is_singleton", False)

    @property
    def queryset(self):
        return self.model.objects.all()

    @cache
    def get_serializer_class(self):
        class Serializer(self.serializer_class):
            __str__ = serializers.SerializerMethodField(method_name="get_str")

            class Meta:
                model = self.model
                fields = None if self.exclude else self.fields
                exclude = self.exclude

            def get_str(self, obj):
                return str(obj)

        return Serializer

    @cache
    def get_viewset_class(self):
        if not self.viewset_class:
            return None

        class ViewSet(self.viewset_class):
            resource_id = self.resource_id
            queryset = self.queryset
            serializer_class = self.get_serializer_class()
            search_fields = self.get_search_fields()

        if self.permission_classes is not None:
            ViewSet.permission_classes = self.permission_classes

        if self.filterset_class is not None:
            ViewSet.filterset_class = self.get_filterset_class()

        return ViewSet

    @cache
    def get_filterset_class(self):
        class ViewFilterSet(self.filterset_class):
            class Meta:
                model = self.model
                fields = self.fields

        return ViewFilterSet

    def serialize(self, request=None):
        fields = {}
        _meta = self.model._meta

        # Get information about the model fields
        info = model_meta.get_field_info(self.model)

        is_user_model = self.model is get_user_model()

        result = {
            "resource_id": self.resource_id,
            "model_name": self.model_name,
            "verbose_name": _meta.verbose_name,
            "verbose_name_plural": _meta.verbose_name_plural,
            "app_label": _meta.app_config.label,
            "app_verbose_name": _meta.app_config.verbose_name,
        }

        if self.is_singleton:
            result["is_singleton"] = True

        if is_user_model:
            result["is_user_model"] = True

        # Parse non-relational fields
        for field in {"id": info.pk, **info.fields}.values():
            default = getattr(field, "default", None)

            # JSON fields often use list or dict constructor as defaults
            if default is list:
                default = []
            if default is dict:
                default = {}

            fields[field.name] = {
                "type": field.__class__.__name__,
                "label": getattr(field, "verbose_name", ""),
                "help_text": getattr(field, "help_text", ""),
                "editable": getattr(field, "editable", True),
                "error_messages": getattr(field, "error_messages", {}),
                "choices": getattr(field, "choices", None),
                "validation": {
                    "required": not getattr(field, "null", False)
                    and not getattr(field, "blank", False),
                    "min_length": getattr(field, "min_length", None),
                    "max_length": getattr(field, "max_length", None),
                },
            }
            if hasattr(field, "json_schema"):
                fields[field.name]["schema"] = field.json_schema
            if hasattr(field, "media_field"):
                fields[field.name]["media_field"] = field.media_field
            if hasattr(field, "aspect_field"):
                fields[field.name]["aspect_field"] = field.aspect_field
            if field.primary_key:
                fields[field.name]["primary_key"] = True
            if is_jsonable(default):
                fields[field.name]["default"] = default

        # Parse relational fields.
        for field in info.forward_relations.values():
            if field.has_through_model:
                # Don't add m2m fields that have a custom through model.
                continue
            model_field = field.model_field
            fields[model_field.name] = {
                "type": model_field.__class__.__name__,
                "is_relation": True,
                "to_many": field.to_many,
                "related_model": model_field.related_model._meta.model_name,
                "resource_id": get_resource_id(model_field.related_model),
                "label": getattr(model_field, "verbose_name", ""),
                "help_text": getattr(model_field, "help_text", ""),
                "editable": getattr(model_field, "editable", True),
                "error_messages": getattr(model_field, "error_messages", {}),
                "default": [] if field.to_many else None,
                "validation": {
                    "required": not getattr(model_field, "null", False)
                    and not getattr(model_field, "blank", False),
                },
            }
            if hasattr(model_field, "file_type"):
                fields[model_field.name]["validation"]["file_type"] = model_field.file_type

        result["fields"] = fields

        return result

    def get_admin_config(self, request=None):
        try:
            admin_class = admin.site.get_model_admin(self.model)

            return {
                "fields": admin_class.fields and camelize_list(admin_class.fields),
                "sidebar_fields": hasattr(admin_class, "sidebar_fields") and camelize_list(admin_class.sidebar_fields) or [],
                "exclude": admin_class.exclude and camelize_list(admin_class.exclude),
                "readonly_fields": admin_class.readonly_fields and camelize_list(admin_class.readonly_fields),
                "list_display": admin_class.list_display
                and camelize_list(admin_class.list_display),
                "list_display_links": admin_class.list_display_links
                and camelize_list(admin_class.list_display_links),
                "list_filter": admin_class.list_filter
                and camelize_list(admin_class.list_filter),
                "list_per_page": admin_class.list_per_page,
                "inlines": self.get_admin_inlines(admin_class),
                "permissions": admin_class.get_model_perms(request),
                "enable_search": getattr(admin_class, "enable_search", False),
                "field_config": getattr(admin_class, "field_config", {}),
                "sortable_by": admin_class.sortable_by and camelize_list(admin_class.sortable_by),
            }
        except NotRegistered:
            return None

    def get_admin_inlines(self, admin_class):
        inlines = []

        for inline in admin_class.inlines:
            fk = _get_foreign_key(
                parent_model=self.model,
                model=inline.model,
                fk_name=inline.fk_name,
                can_fail=False,
            )
            inlines += [
                {
                    "resource_id": get_resource_id(inline.model),
                    "fk_name": fk.name,
                    "can_delete": inline.can_delete,
                    "can_add": getattr(inline, "can_add", True),
                    "fields": camelize_list(getattr(inline, "fields", None) or []),
                    "extra": inline.extra,
                    "min_num": inline.min_num,
                    "max_num": inline.max_num,
                }
            ]

        return inlines

    def get_fields(self):
        """
        Returns the model fields for the content type's allowed fields.
        """
        allowed_fields = []

        for field in self.model._meta.get_fields():
            if (self.fields == '__all__' or field.name in self.fields) and (not self.exclude or field.name not in self.exclude):
                allowed_fields.append(field)

        return allowed_fields

    def get_search_fields(self):
        """
        Returns a list of search field names.

        By default, all CharField fields that are also included in the `fields` list are made searchable.
        """
        _search_fields = []
        _model_fields = self.model._meta.fields

        if self.search_fields == "__all__":
            for field in _model_fields:
                if field.__class__ is models.CharField:
                    _search_fields.append(field.name)
        elif self.search_fields == "__fields__":
            for field in _model_fields:
                _is_included_field = (
                    self.fields == "__all__" or field.name in self.fields
                )
                if _is_included_field and field.__class__ is models.CharField:
                    _search_fields.append(field.name)
        elif isinstance(self.search_fields, list):
            _search_fields = self.search_fields
        else:
            raise TypeError(
                "search_fields must be either a list of strings or one of the special values `__all__` or `__fields__`."
            )

        return _search_fields


def register(resource_id: str = None):
    """
    Decorator for registering a content type.
    """

    def decorator(content_type_model: Type[ContentType]):
        content_type = content_type_model(resource_id=resource_id)

        registry.register(content_type.resource_id, content_type)

        return content_type_model

    return decorator
