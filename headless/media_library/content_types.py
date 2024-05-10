from headless.core import ContentType, register

from .models import Media, Folder


@register(resource_id="media-library/items")
class MediaContentType(ContentType):
    model = Media


@register(resource_id="media-library/folders")
class FolderContentType(ContentType):
    model = Folder
