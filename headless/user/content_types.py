from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

from headless.core import ContentType, register


@register(resource_id="users")
class UserContentType(ContentType):
    model = get_user_model()
    exclude = ["password", "username"]


@register(resource_id="permissions")
class PermissionContentType(ContentType):
    model = Permission


@register(resource_id="groups")
class GroupContentType(ContentType):
    model = Group
