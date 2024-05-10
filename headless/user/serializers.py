from django.contrib.auth import get_user_model

from headless.rest.serializers import ContentSerializer

User = get_user_model()


class UserSerializer(ContentSerializer):
    class Meta:
        model = User
        exclude = ["password"]
