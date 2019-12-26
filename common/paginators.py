from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
# from portal.curr_settings import CURR_FULL_SITE


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20
    page_query_param = 'page'

    # def get_paginated_response(self, data):
    #     next_page = self.get_next_link()
    #     prev_page = self.get_previous_link()
    #
    #     if next_page:
    #         next_page = next_page[len(CURR_FULL_SITE):]
    #     if prev_page:
    #         prev_page = prev_page[len(CURR_FULL_SITE):]
    #
    #     return Response({
    #         'links': {
    #             'next': next_page,
    #             'previous': prev_page
    #         },
    #         'count': self.page.paginator.count,
    #         'results': data
    #     })


class AdvisorBidPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = 'page_size'
    max_page_size = 40
    page_query_param = 'page'

