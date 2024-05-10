from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.viewsets import ModelViewSet

from headless.registry import registry


class ContentViewSet(ModelViewSet):
    lookup_field = "id"
    resource_id = None

    def retrieve(self, request, *args, **kwargs):
        """
        Disable this endpoint for singletons. They should use
        the list endpoint instead.
        """
        if self.is_singleton:
            raise MethodNotAllowed(
                method="GET",
                detail="Singleton objects do not support the retrieve endpoint.",
            )

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        We overwrite the update method to support singletons. If a singleton
        doesn't exist it will be created.
        """
        if self.is_singleton:
            try:
                super().update(request, *args, **kwargs)
            except NotFound:
                self.create(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        We overwrite the list method to support singletons. If a singleton
        doesn't exist this will raise a NotFound exception.
        """
        if self.is_singleton:
            return super().retrieve(request, *args, **kwargs)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        ct = registry.get(self.resource_id)

        if hasattr(ct, "perform_create"):
            instance = ct.perform_create(self.request, serializer)
        else:
            instance = serializer.save()

        if hasattr(instance, "edited_by"):
            instance.edited_by = self.request.user
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=ADDITION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_update(self, serializer):
        ct = registry.get(self.resource_id)

        if hasattr(ct, "perform_update"):
            instance = ct.perform_create(self.request, serializer)
        else:
            instance = serializer.save()

        if hasattr(instance, "edited_by"):
            instance.edited_by = self.request.user
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=CHANGE,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_destroy(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=DELETION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

        ct = registry.get(self.resource_id)

        if hasattr(ct, "perform_destroy"):
            ct.perform_destroy(self.request, instance)
        else:
            instance.delete()

    def get_object(self):
        """
        We overwrite this method to add support for singletons.
        If a singleton doesn't exist it will raise a NotFound exception.
        """
        if self.is_singleton:
            try:
                return self.get_queryset().get()
            except self.queryset.model.DoesNotExist:
                raise NotFound()

        return super().get_object()

    @property
    def is_singleton(self):
        return getattr(self.get_queryset().model, "is_singleton", False)
