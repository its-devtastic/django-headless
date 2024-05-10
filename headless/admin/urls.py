from rest_framework.routers import SimpleRouter

from .views import AdminViewSet

router = SimpleRouter(trailing_slash=False)

router.register("", AdminViewSet, "admin")

urlpatterns = router.urls
