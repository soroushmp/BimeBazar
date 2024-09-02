from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Book, Rating


class BookSerializer(serializers.ModelSerializer):
    """
    List of books serializer with extra fields
    """
    bookmarks_count = serializers.SerializerMethodField()
    is_bookmark = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'bookmarks_count', 'is_bookmark', ]
        read_only_fields = ["id"]

    def get_bookmarks_count(self, obj):
        """
        Get bookmarked users count for a specific book.
        """
        return obj.bookmarks.count()

    def get_is_bookmark(self, obj):
        """
            Check if requested user has bookmarked this book or not.
            note: Needs Authentication
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.books.filter(id=obj.id).exists()
        else:
            return 'Login Required'


class BookDetailSerializer(serializers.ModelSerializer):
    """
        Details of a single book by its ID serializer with extra fields
    """
    reviews_count = serializers.SerializerMethodField()
    scores_count = serializers.SerializerMethodField()
    scores_mean = serializers.SerializerMethodField()
    scores_count_group_by_number = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'summary', 'reviews_count', 'scores_count', 'scores_mean',
                  'scores_count_group_by_number', 'ratings']
        read_only_fields = ["id"]

    def get_reviews_count(self, obj):
        """
        Get queryset of Rating instances with reviews field not null and not empty (blank).
        """
        return obj.ratings.filter(review__isnull=False).exclude(review='').count()

    def get_scores_count(self, obj):
        """
            Get queryset of Rating instances with scores field not null.
        """
        return obj.ratings.filter(score__isnull=False).count()

    def get_scores_mean(self, obj):
        """
            Get average scores using Rating instances with scores field not null.
        """
        return obj.ratings.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg']

    def get_scores_count_group_by_number(self, obj):
        """
            Get count of unique scores using Rating instances with scores field not null.
        """
        return obj.ratings.filter(score__isnull=False).values('score').annotate(
            count=Count('score')).values('score', 'count')

    def get_ratings(self, obj):
        """
        Returns Serialized list of Rating instances.
        """
        return RatingSerializer(obj.ratings.all(), many=True).data


class RatingSerializer(serializers.ModelSerializer):
    """
        Rating instance serializer
    """

    class Meta:
        model = Rating
        fields = ['user', 'book', 'score', 'review']
        extra_kwargs = {
            'book': {'required': True, 'help_text': "Book Id Integer"},
            'user': {'required': False, 'help_text': "User Id Integer"},
            'score': {'required': False, 'help_text': "Score Integer From 1 to 5"},
            'review': {'required': False, 'help_text': "Review Text"}
        }

    def validate(self, data):
        if not data.get('score') and not data.get('review'):
            raise serializers.ValidationError("At Least One of Score or Review Must Be Filled!")
        return data


class RegisterLoginSerializer(serializers.Serializer):
    """
        Register/Login data serializer
    """
    email = serializers.EmailField(required=True, help_text="Email Address")
    password = serializers.CharField(required=True, min_length=8, help_text="Password Min 8 Characters")

    def validate(self, data):
        email = data['email']
        password = data['password']

        user, created = User.objects.get_or_create(username=email)

        if not created:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid Credentials!")

        if created:
            user.set_password(password)
            user.save()

        refresh = RefreshToken.for_user(user)

        return {
            'user_id': user.id,
            'email': user.username,
            'created': created,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class BookmarkSerializer(serializers.Serializer):
    """
        Bookmark data serializer
    """
    book = serializers.IntegerField(required=True, help_text="Book Id Integer")

    def validate(self, data):
        book_id = data.get('book')
        user = self.context.get('request').user
        try:
            Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError(f"Book With ID '{book_id}' Does Not Exist!")

        if user.ratings.filter(book_id=book_id).exists():
            raise serializers.ValidationError(f"Book With ID '{book_id}' Is Have a Rating!")
        return data
