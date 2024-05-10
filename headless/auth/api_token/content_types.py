from headless.core import ContentType, register

from .models import ApiToken, ApiTokenUsage


@register(resource_id="api-tokens")
class ApiTokenContentType(ContentType):
    model = ApiToken


@register(resource_id="api-token-usage")
class ApiTokenUsageContentType(ContentType):
    model = ApiTokenUsage
