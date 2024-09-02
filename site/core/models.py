from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    bookmarks = models.ManyToManyField(User, related_name='books')

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True)
    review = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'User: {self.user.email} | Book: {self.book.title}'
