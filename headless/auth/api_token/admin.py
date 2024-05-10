from headless import admin
from .models import ApiToken, ApiTokenUsage


class ApiTokenUsageInline(admin.StackedInline):
    model = ApiTokenUsage
    fields = ["timestamp", "method", "path", "query_params"]
    can_delete = False
    can_add = False


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    readonly_fields = ["last_used", "edited_by", "modified_at", "created_at", "token"]
    list_display = ["description", "last_used", "created_at", "is_enabled"]
    fields = ["description", "full_access", "read_only_access", "permissions"]
    sidebar_fields = ["last_used", "is_enabled", "token"]
    inlines = [ApiTokenUsageInline]
