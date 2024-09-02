from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from core.views import BookList, BookDetail, BookmarkManageView, RegisterLoginView, RatingManageView

# Documentation Configs
schema_view = get_schema_view(
    openapi.Info(
        title="B2Reads",
        default_version='v1',
        description="Api Endpoint Documentation",
        contact=openapi.Contact(email="sorm1379@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny, ],
)

urlpatterns = [
    # Admin Dashboard
    path('admin/', admin.site.urls),

    # Register and Login Endpoint
    path('register-login/', RegisterLoginView.as_view(), name='register-login'),

    # Get Data Endpoint(s)
    path('books/', BookList.as_view(), name='book-list'),
    path('books/<int:id>/', BookDetail.as_view(), name='book-detail'),

    # Post Data Endpoint(s)
    path('bookmarks/', BookmarkManageView.as_view(), name='bookmark-manage'),
    path('ratings/', RatingManageView.as_view(), name='rating-create-or-update'),

    # Documentation
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
