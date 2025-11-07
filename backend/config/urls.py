"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from apps.core.health_views import health_check, health_check_detailed
from apps.users.views.auth_views import login_view, register_view, logout_view

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # Health checks
    path("api/v1/health/", health_check, name="health_check"),
    path("api/v1/health/detailed/", health_check_detailed, name="health_check_detailed"),

    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Custom authentication endpoints (for frontend)
    path("api/v1/auth/login/", login_view, name="auth_login"),
    path("api/v1/auth/register/", register_view, name="auth_register"),
    path("api/v1/auth/logout/", logout_view, name="auth_logout"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="auth_refresh"),

    # JWT authentication (original endpoints)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # App URLs (v1 API)
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.vouchers.urls")),
]

# Django Debug Toolbar URLs (only in development)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
