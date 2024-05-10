from rest_framework import pagination
from rest_framework.response import Response

from core import settings


class PageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "page"
    page_size = getattr(settings, "HEADLESS", {}).get("PAGE_SIZE", 10)
    max_page_size = getattr(settings, "HEADLESS", {}).get("MAX_PAGE_SIZE", 100)

    def get_paginated_response(self, data):
        absolute_uri = self.request.build_absolute_uri()
        return Response(
            {
                "pagination": {
                    "count": self.page.paginator.count,
                    "pages": self.page.paginator.num_pages,
                    "current": self.page.number,
                    "limit": self.page_size,
                    "links": {
                        "self": absolute_uri,
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                    },
                },
                "data": data,
            }
        )
