from mainsite.models import Book
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from utils.helpers.responses import SuccessResponse, ErrorResponse
from rest_framework import status
from utils.views import CustomPaginator
from django.core.cache import cache # to be implemented if needed
from django.db.models import Count, Value,Q,F
from django.db.models.functions import Concat
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .serialisers import BookSerializer 
from functools import reduce
from operator import or_

from django.db import DatabaseError
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError, APIException
from rest_framework.throttling import AnonRateThrottle,SimpleRateThrottle



PAGINATOR = CustomPaginator()



class HealthCheckAPI(APIView):
    permission_classes = (AllowAny,)
    
    def get(self ,request, version, format=None):
        return SuccessResponse({"status":"ok"}, status=status.HTTP_200_OK)


class GetLibraryAPI(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle,]

    
    @extend_schema( # source : https://github.com/tfranzel/drf-spectacular?tab=readme-ov-file
        parameters=[
            OpenApiParameter(name='book_id', description='book id', required=False, type=int,
                            examples=[
                                OpenApiExample(
                                    name='book_id example 1',
                                    summary='book_id example 1',
                                    description='',
                                    value=[1,2,3]
                                    )]),
            OpenApiParameter(name='author_name', description='author names', required=False, type=str,
                            examples=[
                                OpenApiExample(
                                    name='author_name example 1',
                                    summary='author_name example 1',
                                    description='',
                                    value=['Doyle','Shelley']
                                    )]),
            OpenApiParameter(name='mime_type', description='mime type present with the book', required=False, type=str,
                            examples=[
                                OpenApiExample(
                                    name='book_title example 1',
                                    summary='book_title example 1',
                                    description='',
                                    value=['child']
                                    )]),
            OpenApiParameter(name='book_title', description='Title of the book', required=False, type=str,
                            examples=[
                                OpenApiExample(
                                    name='book_title example 1',
                                    summary='book_title example 1',
                                    description='',
                                    value=['child']
                                    )]),
            OpenApiParameter(name='language', description='launguage', required=False, type=str,
                            examples=[
                    OpenApiExample(
                        name='language example 1',
                        summary='language example 1',
                        description='',
                        value=['en','fr']
                    ),
                    OpenApiExample(
                        name='language example 2',
                        summary='language example 2',
                        description='',
                        value=['en']
                    ),
                ],),
            OpenApiParameter(name='topic', description='topic', required=False, type=str,
                             examples=[
                    OpenApiExample(
                        name='topic example 1',
                        summary='topic example 1',
                        description='',
                        value=['child','infant']
                    ),
                    OpenApiExample(
                        name='topic example 2',
                        summary='topic example 2',
                        description='',
                        value=['child']
                    ),
                ],),
        ],
        # override default docstring extraction
        description='This api has dealings with the fetching of books corresponding to the searches made. If there is no body params send in the request then it will behave as a response with the complete set of books present in the library present with us',
        # provide Authentication class that deviates from the views default
        auth=None,
        # change the auto-generated operation name
        operation_id='bookLibrary_fetchBooks',
        # or even completely override what AutoSchema would generate. Provide raw Open API spec as Dict.
        operation=None,
        responses=BookSerializer
    )
    def post(self, request, version, format=None):
        try:
            book_ids = request.data.get('book_id', None)
            languages = request.data.get('language', None)
            mime_types = request.data.get('mime_type', None)
            topics = request.data.get('topic', None) # data from either bookshelf or subject
            author_name = request.data.get('author_name', None) #case insensitive
            book_title = request.data.get('title', None) #case insensitive

            
            books_chunk = Book.objects.all()

            if book_ids:
                book_ids = book_ids if isinstance(book_ids, list) else [book_ids]
                books_chunk = books_chunk.filter(gutenberg_id__in=book_ids)
            
            if languages:
                languages = languages if isinstance(languages, list) else [languages]

                books_chunk = books_chunk.filter(booklanguages__language__code__in=languages).distinct()
            if mime_types:
                mime_types = mime_types if isinstance(mime_types, list) else [mime_types]
                
                books_chunk = books_chunk.filter(format__mime_type__in=mime_types).distinct()

            if topics:
                topics = topics if isinstance(topics, list) else [topics]
                topic_filters = reduce(
                    or_, 
                    [
                        Q(booksubjects__subject__name__icontains=topic) | Q(bookbookshelves__bookshelf__name__icontains=topic)
                        for topic in topics
                    ]
                    )
                books_chunk = books_chunk.filter(topic_filters).distinct()
            if author_name:
                author_name = author_name if isinstance(author_name, list) else [author_name]
                
                author_filters = reduce(
                    or_, 
                    [
                        Q(bookauthors__author__name__icontains=author)
                        for author in author_name
                    ]
                    )
                books_chunk = books_chunk.filter(author_filters).distinct()
            if book_title:
                book_title = book_title if isinstance(book_title, list) else [book_title]
                book_filters = reduce(
                    or_, 
                    [
                        Q(title__icontains=title)
                        for title in book_title
                    ]
                    )
                books_chunk = books_chunk.filter(book_filters).distinct()
            
            try:
                context = books_chunk.annotate(
                    book_title = F('title'),
                    book_id = F("gutenberg_id"),
                    author_name = ArrayAgg( #source : https://docs.djangoproject.com/en/5.1/ref/contrib/postgres/aggregates/ and chatgpt
                        Concat(
                            F('bookauthors__author__name'),
                            Value(' ('),
                            F('bookauthors__author__birth_year'),
                            Value(' - '),
                            F('bookauthors__author__death_year'),
                            Value(' )'),
                            output_field=models.CharField()
                            ),
                        distinct = True
                        ),
                        available_formats= ArrayAgg(
                            Concat(
                                Value('Mine Type : '),
                                F('format__mime_type'),
                                Value(' --  Url: '),
                                F('format__url'),),
                            distinct=True,),
                        author_count=Count('bookauthors__author', distinct=True),
                        languages=ArrayAgg(
                            F('booklanguages__language__code'),
                            distinct = True,
                            )
                            ).values(
                                "book_id",
                                "title",
                                "author_name",
                                "languages",
                                "author_count",
                                "available_formats",
                                "download_count"
                                ).order_by(F('download_count').desc(nulls_last=True)) 
            except DatabaseError as e:
                raise APIException(detail=f"Database error occurred: {str(e)}")

            try:
                PAGINATOR.page_size = 25

                books_paginated = PAGINATOR.paginate_queryset(context,request)
                serializer_response = PAGINATOR.get_paginated_response(books_paginated)
            except Exception as e:
                raise APIException(detail=f"Pagination error occurred: {str(e)}")
            return SuccessResponse(serializer_response.data, status=status.HTTP_200_OK)
        except APIException as e:
            return ErrorResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return ErrorResponse({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

