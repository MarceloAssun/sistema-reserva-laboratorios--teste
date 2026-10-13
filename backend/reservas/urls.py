from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import AgendaView, DisponibilidadeView, ReservaViewSet

router = DefaultRouter()
router.register('reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('agenda/', AgendaView.as_view(), name='agenda'),
    path('disponibilidade/', DisponibilidadeView.as_view(), name='disponibilidade'),
]
urlpatterns += router.urls
