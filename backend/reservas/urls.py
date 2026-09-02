from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import DisponibilidadeView, ReservaViewSet

router = DefaultRouter()
router.register('reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('disponibilidade/', DisponibilidadeView.as_view(), name='disponibilidade'),
]
urlpatterns += router.urls
