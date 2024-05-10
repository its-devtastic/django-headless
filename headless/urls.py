from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import HealthCheckView, RootView

urlpatterns = (
    [
        path("", RootView.as_view()),
        path("_health", HealthCheckView.as_view()),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
