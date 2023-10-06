from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination

DEFAULT_PAGE_SIZE = 5


class PageNumberPaginationWithLimit(pagination.PageNumberPagination):
    """Custom pagination class with page numbers with limit."""

    page_size = getattr(
        settings,
        "REST_FRAMEWORK",
        {},
    ).get("PAGE_SIZE", DEFAULT_PAGE_SIZE)
    page_size_query_param = "limit"
    page_size_query_description = _(
        "Number of results to return per page. "
        'Set equal "false" to turn off pagination'
    )
