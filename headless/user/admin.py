from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from headless import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ["username", "password"]
    fields = [
        "profile_picture",
        "first_name",
        "last_name",
        "email",
        "locale",
        "timezone",
    ]
    sidebar_fields = [
        "last_login",
        "date_joined",
        "is_superuser",
        "is_staff",
        "is_active",
        "groups",
        "user_permissions",
    ]
    readonly_fields = ["last_login", "date_joined", "modified_at", "created_at"]
    list_display = [
        "thumbnail",
        "name",
        "email",
        "is_staff",
        "date_joined",
        "last_login",
    ]
    list_display_links = ["thumbnail", "name", "email"]

    @admin.display(description=_("name"))
    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="")
    def thumbnail(self, obj):
        return obj.profile_picture and format_html(
            f'<img style="width: 48px; height: 48px; object-fit: cover; border-radius: 100%;" src="{obj.profile_picture}" />'
        )
