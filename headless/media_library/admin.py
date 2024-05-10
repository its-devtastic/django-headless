from headless import admin
from .models import Media, Folder


@admin.register(Folder)
class MediaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "parent",
        "created_at",
    ]
    list_display_links = [
        "name",
    ]
    enable_search = True


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = [
        "file",
        "name",
        "type",
        "size",
        "created_at",
    ]
    fields = ["crop", "file", "name", "tags"]
    sidebar_fields = ["type", "alt_text", "folder"]
    list_display_links = ["file", "name"]
    enable_search = True
    field_config = {"size": {"format": "file_size"}}
