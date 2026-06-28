"""
URL configuration for digital_msharika project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from tenants.views import (
    AboutView,
    ContactView,
    CustomLoginView,
    DashboardView,
    EventsView,
    LandingView,
    MinistriesView,
    PasswordResetRequestView,
    PasswordResetSetView,
    PasswordResetVerifyView,
    SignupVerifyView,
    SignupView,
    TenantCreateView,
    logout_view,
)

from api.views import BriqSmsWebhookView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", LandingView.as_view(), name="landing"),
    path("about/", AboutView.as_view(), name="about"),
    path("events/", EventsView.as_view(), name="events"),
    path("ministries/", MinistriesView.as_view(), name="ministries"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("dashboard/", DashboardView.as_view(), name="home"),
    path("tenants/create/", TenantCreateView.as_view(), name="tenant-create"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password/reset/new/", PasswordResetSetView.as_view(), name="password-reset-set"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("signup/verify/", SignupVerifyView.as_view(), name="signup-verify"),
    path("webhooks/briq/sms/", BriqSmsWebhookView.as_view(), name="briq-sms-webhook"),
    path("logout/", logout_view, name="logout"),
    path("members/", include("members.urls")),
    path("fellowships/", include("fellowships.urls")),
    path("pledges/", include("pledges.urls")),
    path("content/", include("content_app.urls")),
    path("api/", include("api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
