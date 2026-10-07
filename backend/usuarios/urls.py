from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, UserViewSet

router = DefaultRouter()
router.register('usuarios', UserViewSet, basename='usuario')

urlpatterns = [path('auth/me/', CurrentUserView.as_view(), name='current-user')] + router.urls
