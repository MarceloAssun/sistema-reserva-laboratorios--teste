from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, RegisterView, UserViewSet

router = DefaultRouter()
router.register('usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
] + router.urls
