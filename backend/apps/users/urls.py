"""
URL routing for users app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
