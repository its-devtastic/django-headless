from django.apps import apps
from django.utils import timezone
from django.utils.encoding import smart_str
from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header


class ApiTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if not self.is_app_installed():
            return None

        model = self.get_model()

        bearer = self.get_token(request)

        if not bearer:
            return None

        try:
            token = model.objects.get(token=bearer, is_enabled=True)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("API token authentication failed")

        token.last_used = timezone.now()
        token.save()

        return token, bearer

    def get_token(self, request):
        auth = get_authorization_header(request).split()
        if not auth or smart_str(auth[0].lower()) != "bearer":
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed()

        return auth[1].decode()

    def authenticate_header(self, request):
        return "Bearer: api"

    def get_model(self):
        return apps.get_model("headless_api_token.ApiToken")

    def is_app_installed(self):
        return apps.is_installed("headless.auth.api_token")
