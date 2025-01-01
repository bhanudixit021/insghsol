from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math
from utils.helpers import constants
# Create your views here.


class CustomPaginator(PageNumberPagination):
    page = constants.DEFAULT_PAGE
    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
			'next': self.get_next_link(),
			'previous': self.get_previous_link(),
            'total': self.page.paginator.count,
            'total_pages': math.ceil(self.page.paginator.count/int(self.request.GET.get('page_size', self.page_size))) if self.page.paginator.count else 0,
            'page': int(self.request.GET.get('page', constants.DEFAULT_PAGE)), # can not set default = self.page
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })