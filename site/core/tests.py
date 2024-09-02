from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Rating
from .serializers import BookSerializer, BookDetailSerializer, RatingSerializer


class BookViewsTest(APITestCase):

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the test user
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Add Authorization header to the client
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        # Create test books
        self.book1 = Book.objects.create(title='Book 1', author='Author 1')
        self.book2 = Book.objects.create(title='Book 2', author='Author 2')

        # Create test URL paths
        self.book_list_url = reverse('book-list')  # Assuming you have named the URL 'book-list'
        self.book_detail_url = reverse('book-detail', args=[self.book1.id])
        self.bookmark_manage_url = reverse('bookmark-manage')
        self.rating_manage_url = reverse('rating-manage')

    def test_get_all_books(self):
        response = self.client.get(self.book_list_url)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        # Test caching
        cache_key = 'all_books'
        cached_books = cache.get(cache_key)
        self.assertIsNotNone(cached_books)
        self.assertEqual(cached_books, serializer.data)

    def test_get_book_detail(self):
        response = self.client.get(self.book_detail_url)
        book = Book.objects.get(id=self.book1.id)
        serializer = BookDetailSerializer(book)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        # Test caching
        cache_key = f'book_detail_{self.book1.id}'
        cached_book = cache.get(cache_key)
        self.assertIsNotNone(cached_book)
        self.assertEqual(cached_book, serializer.data)

    def test_post_bookmark_add_and_remove(self):
        # Add Bookmark
        data = {'book': self.book1.id}
        response = self.client.post(self.bookmark_manage_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Bookmark Added.')
        self.assertTrue(self.user.books.filter(id=self.book1.id).exists())

        # Remove Bookmark
        response = self.client.post(self.bookmark_manage_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Bookmark Removed.')
        self.assertFalse(self.user.books.filter(id=self.book1.id).exists())

        # Ensure cache is invalidated
        self.assertIsNone(cache.get('all_books'))
        self.assertIsNone(cache.get(f'book_detail_{self.book1.id}'))

    def test_post_rating_create_and_update(self):
        # Create Rating
        data = {
            'book': self.book1.id,
            'score': 5,
            'review': 'Great book!'
        }
        response = self.client.post(self.rating_manage_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rating = Rating.objects.get(book=self.book1, user=self.user)
        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.review, 'Great book!')

        # Update Rating
        data['score'] = 4
        response = self.client.post(self.rating_manage_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rating.refresh_from_db()
        self.assertEqual(rating.score, 4)

        # Ensure bookmark is removed
        self.assertFalse(self.user.books.filter(id=self.book1.id).exists())

        # Ensure cache is invalidated
        self.assertIsNone(cache.get('all_books'))
        self.assertIsNone(cache.get(f'book_detail_{self.book1.id}'))

    def test_post_register_login(self):
        # Register and login new user
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(reverse('register-login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['created'])  # Since the user is created and logged in
