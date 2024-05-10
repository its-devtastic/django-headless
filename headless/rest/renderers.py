from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class DefaultRenderer(CamelCaseJSONRenderer):
    """
    Default JSON renderer based on CamelCaseJSONRenderer.
    """

    media_type = "application/json"
    format = "json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        res = renderer_context["response"]
        view = renderer_context["view"]
        is_paginated = getattr(view, "pagination_class", None) is not None
        is_exception = res.exception

        # Current view action: either retrieve, create, partial_update, list or delete
        action = getattr(view, "action", None)

        result = data

        if not is_exception:
            # Paginated responses are already properly formatted by the pagination class
            if action == "list" and is_paginated:
                result = data

            # Handle non-paginated lists
            if action == "list" and not is_paginated:
                result["data"] = data

            # Handle single documents
            if action in ["retrieve", "create", "partial_update"]:
                result = data

        return super().render(result, accepted_media_type, renderer_context)
