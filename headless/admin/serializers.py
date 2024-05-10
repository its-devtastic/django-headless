import json

from django.contrib.admin.models import LogEntry
from rest_framework import serializers

from headless.utils import get_resource_id


class LogEntrySerializer(serializers.ModelSerializer):
    action_flag = serializers.SerializerMethodField()
    object_resource_id = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()
    change_message = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "action_time",
            "object_id",
            "object_repr",
            "object_resource_id",
            "changes",
            "change_message",
            "action_flag",
        ]

    def get_action_flag(self, instance):
        return {1: "ADDITION", 2: "CHANGE", 3: "DELETION"}.get(
            instance.action_flag, None
        )

    def get_object_resource_id(self, instance):
        model = instance.content_type.model_class()

        # If model is no longer installed return None.
        if not model:
            return None

        return get_resource_id(model)

    def get_changes(self, instance):
        try:
            return json.loads(instance.change_message)
        except json.decoder.JSONDecodeError:
            return []

    def get_change_message(self, instance):
        return instance.get_change_message()
