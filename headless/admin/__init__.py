from django.contrib.admin import *

from .widgets import RecentActivityWidget

default_app_config = "headless.admin.apps.DjangoHeadlessAdminConfig"


class AdminSite(AdminSite):
    dashboard_widgets = [RecentActivityWidget()]


admin_site = AdminSite()


class ModelAdmin(ModelAdmin):
    # We set a lower limit than Django's default of 100
    list_per_page = 20

    # Instead of using the `search_fields` attribute we use a simple
    # boolean to indicate if searching is enabled. Searching will
    # always use DRF's search filter and can be configured using the
    # `search_fields` attribute of the content type class.
    enable_search = True

    # Fields to display in the sidebar of the edit screen in Django Headless Admin.
    sidebar_fields = []

    def save_model(self, request, obj, form, change):
        if hasattr(obj, "edited_by"):
            obj.edited_by = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        is_singleton = getattr(self.model, "is_singleton", False)

        # Don't allow to add more than one singleton object.
        if is_singleton and self.model.objects.get():
            return False

        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        is_singleton = getattr(self.model, "is_singleton", False)

        if is_singleton:
            return False

        return super().has_add_permission(request)

    def render_change_form(self, request, context, *args, **kwargs):
        is_singleton = getattr(self.model, "is_singleton", False)

        context["show_save_and_add_another"] = not is_singleton

        return super().render_change_form(request, context, *args, **kwargs)
