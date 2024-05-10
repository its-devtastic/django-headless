from rest_framework import serializers

from headless.media_library.models import Folder


class FolderPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name"]
