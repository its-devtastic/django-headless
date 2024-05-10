from django.apps import AppConfig

from headless.utils import is_runserver


class DjangoHeadlessConfig(AppConfig):
    name = "headless"
    label = "headless"
    initialized = False

    def ready(self):
        from django.utils.module_loading import autodiscover_modules

        from .core import registry
        from .utils import log

        if is_runserver() and not self.initialized:
            log(":rocket:", "Starting Django Headless CMS")
            log(":mag:", "Discovering content types...")
            autodiscover_modules("content_types")
            log(
                ":white_check_mark:",
                f"[green]Found {len(registry)} contenttypes[/green]",
            )

            self.initialized = True
