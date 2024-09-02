from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from B2Reads.settings import CACHE_TTL
from .models import Book, Rating
from .serializers import BookSerializer, RatingSerializer, RegisterLoginSerializer, BookDetailSerializer, \
    BookmarkSerializer


class BookList(APIView):
    """
    Returns list of all books with get request.
    """

    def get(self, request, format=None):
        cache_key = 'all_books'
        cache_time = CACHE_TTL
        books = cache.get(cache_key)

        if not books:
            books = Book.objects.all()
            serializer = BookSerializer(books, many=True, context={'request': request})
            books = serializer.data
            cache.set(cache_key, books, cache_time)

        return Response(books)


class BookDetail(APIView):
    """
    Returns a book instance details with get request.
    """

    def get_object(self, id):
        try:
            return Book.objects.get(id=id)
        except Book.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        cache_key = f'book_detail_{id}'
        cache_time = CACHE_TTL
        book = cache.get(cache_key)

        if not book:
            book_instance = self.get_object(id)
            serializer = BookDetailSerializer(book_instance)
            book = serializer.data
            cache.set(cache_key, book, cache_time)

        return Response(book)


class BookmarkManageView(APIView):
    """
        Handle bookmarks with post request, if bookmark for specific book already exists it will be removed,
        otherwise it will be added.
        note: users can't add bookmark for books that rating instance is created before for that user
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BookmarkSerializer,
        responses={
            200: openapi.Response(
                description="Successful Bookmark Manage",
                examples={
                    'application/json': {
                        'detail': 'Bookmark Added.'
                    }
                }
            ),
            400: 'Invalid request'
        },
        security=[{'Bearer': []}]

    )
    def post(self, request, *args, **kwargs):
        serializer = BookmarkSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            book_id = serializer.validated_data['book']
            if user.books.filter(id=book_id).exists():
                user.books.remove(book_id)
                cache.delete('all_books')
                cache.delete(f'book_detail_{book_id}')
                return Response({'detail': 'Bookmark Removed.'}, status=status.HTTP_200_OK)
            else:
                user.books.add(book_id)
                cache.delete('all_books')
                cache.delete(f'book_detail_{book_id}')
                return Response({'detail': 'Bookmark Added.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RatingManageView(APIView):
    """
        Handle ratings with post request, if rating for specific book already exists it will be updated,
        otherwise it will be created.
        note: after updating or creating rating, bookmark for that book will be removed.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'book': openapi.Schema(type=openapi.TYPE_INTEGER, description='Book Id Integer'),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER, description='Score Integer From 1 to 5'),
                'review': openapi.Schema(type=openapi.TYPE_STRING, description='Review Text'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Successful Bookmark Manage",
                examples={
                    'application/json': {
                        "user": 9,
                        "book": 3,
                        "score": 5,
                        "review": "4444"
                    }
                }
            ),
            400: 'Invalid request'
        },
        security=[{'Bearer': []}]

    )
    def post(self, request, *args, **kwargs):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user'] = request.user.id
            book = serializer.validated_data['book']
            rating, created = Rating.objects.get_or_create(
                user_id=user_id,
                book=book,
                defaults={
                    'score': serializer.validated_data.get('score'),
                    'review': serializer.validated_data.get('review')
                }
            )

            if not created:
                rating.score = serializer.validated_data.get('score', rating.score)
                rating.review = serializer.validated_data.get('review', rating.review)
                rating.save()

            if book in request.user.books.all():
                request.user.books.remove(book)

            cache.delete('all_books')
            cache.delete(f'book_detail_{book.id}')

            updated_serializer = RatingSerializer(rating)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterLoginView(APIView):
    """
        Handle authentication with post request, if user with specific email (username) already exists it will be login,
        otherwise it will be created and login.
    """

    @swagger_auto_schema(
        request_body=RegisterLoginSerializer,
        responses={
            200: openapi.Response(
                description="Successful Bookmark Manage",
                examples={
                    'application/json': {
                        'user_id': 1,
                        'email': 'user@example.com',
                        'created': False,
                        'refresh': 'jwt-refresh-token',
                        'access': 'jwt-access-token'
                    }
                }
            ),
            400: 'Bad Request'
        },
        security=[{'Bearer': []}]

    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterLoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = data['email']
            password = request.data['password']

            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
