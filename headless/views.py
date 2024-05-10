from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView


class RootView(TemplateView):
    template_name = "headless/root.html"


class HealthCheckView(APIView):
    """
    A simple health check endpoint.
    """

    def get(self, request, *args, **kwargs):
        return Response(data={"status": "pass"})
