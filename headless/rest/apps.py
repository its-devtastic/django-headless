from django.apps import AppConfig

from headless.utils import is_runserver


class DjangoHeadlessRestConfig(AppConfig):
    name = "headless.rest"
    label = "headless_rest"
    initialized = False

    def ready(self):
        from .router import rest_router
        from ..core import registry
        from ..utils import log

        if is_runserver() and not self.initialized:
            log(":building_construction:", "Setting up REST routes")
            contenttypes = registry.items()

            for [basename, contenttype] in contenttypes:
                view_set = contenttype.get_viewset_class()
                if view_set:
                    log("   |---", f"/{basename}")
                    rest_router.register(basename, view_set)

            self.initialized = True
