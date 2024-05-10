from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.utils.module_loading import import_string
from djangorestframework_camel_case.util import camelize
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from headless.registry import registry
from .serializers import LogEntrySerializer


class AdminViewSet(GenericViewSet):
    permission_classes = [IsAdminUser]

    @action(
        methods=["get"],
        detail=False,
        url_path="admin-site",
        permission_classes=[AllowAny],
    )
    def admin_site(self, request):
        is_admin = request.user.is_superuser
        admin_site = self._get_admin_site()

        data = {
            "site_header": admin_site.site_header,
            "site_title": admin_site.site_title,
            "index_title": admin_site.index_title,
            "site_url": admin_site.site_url,
        }

        if is_admin:
            data["widgets"] = [w.to_json(request) for w in admin_site.dashboard_widgets]

        return Response(data=data)

    @action(
        methods=["get"],
        detail=False,
        url_path="content-types",
        renderer_classes=[JSONRenderer],
    )
    def content_types(self, request):
        content_types = {}
        for name, ct in registry.items():
            admin_config = ct.get_admin_config(request=request)

            content_types[name] = {
                **ct.serialize(request=request),
                "admin": admin_config,
            }

        return Response(
            data={key: camelize(value) for key, value in content_types.items()}
        )

    @action(
        methods=["get"],
        detail=False,
        url_path="recent-actions",
    )
    def recent_actions(self, request):
        log_entries = LogEntry.objects.filter(user=request.user).order_by(
            "-action_time"
        )[:10]
        serializer = LogEntrySerializer(log_entries, many=True)

        return Response(data=serializer.data)

    def _get_admin_site(self):
        module_path = settings.HEADLESS["ADMIN_SITE"]
        return import_string(module_path)
