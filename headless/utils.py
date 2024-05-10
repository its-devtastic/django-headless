import json
import string
import sys

import humps
from django.utils.crypto import get_random_string
from rich.console import Console

from .registry import registry

console = Console()


def log(*args, **kwargs):
    console.print("[cyan][Headless][/cyan]", *args, **kwargs)


def get_resource_id(model):
    """
    Get API ID for a given model.
    """
    return getattr(model._meta, "resource_id", None) or f"{model._meta.model_name}s"


def get_content_type(model):
    """
    Get content type for a given model.
    """
    resource_id = get_resource_id(model)
    return registry.get(resource_id)


def generate_password():
    """
    Generates a strong, 64 char long password.
    """
    return get_random_string(
        64, string.ascii_lowercase + string.ascii_uppercase + string.digits
    )


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def is_runserver():
    """
    Checks if the Django application is started as a server.
    We'll also assume it started if manage.py is not used (e.g. when Django is started using wsgi/asgi).
    The main purpose of this check is to not run certain code on other management commands such
    as `migrate`.
    """
    is_manage_cmd = sys.argv[0].endswith("/manage.py")

    return not is_manage_cmd or sys.argv[1] == "runserver"


def camelize_list(ls):
    try:
        return [camelize_list(i) if isinstance(i, (list, tuple)) else humps.camelize(i) for i in ls]
    except Exception as e:
        log(f"Could not camelize list: {e}")
        return []


def flatten(xss):
    return [x for xs in xss for x in xs]