from django.contrib import admin

from core.models import Book, Rating


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = search_fields = ('title', 'truncated_summary', 'bookmarks_count')

    def bookmarks_count(self, obj):
        """
        Returns count of bookmark users of this book
        """
        return obj.bookmarks.count()

    def truncated_summary(self, obj):
        """
        Returns truncated summary of this book
        """
        return obj.summary[:30] + '...'

    bookmarks_count.short_description = 'Bookmarks Count'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'score', 'review')
    search_fields = ('user__username', 'book__title')
