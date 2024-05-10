from django.conf import settings
from django.utils.html import format_html
from django.utils.module_loading import import_string

from .models import Media


def generate_thumbnail(media: Media, size=48):
    image_loader_path = None

    if not media:
        return None

    url = media.file.url

    try:
        image_loader_path = settings.HEADLESS["IMAGE_LOADER"]
    except (KeyError, AttributeError) as e:
        pass
    if image_loader_path:
        image_loader = import_string(image_loader_path)
        url = image_loader(url, size=size)

    return format_html(
        f'<img src="{url}" style="width: {size}px;height: {size}px;object-fit: cover; border-radius: 4px" alt="{media.name}">'
    )
