from rest_framework.routers import DefaultRouter

from .views import LaboratorioViewSet

router = DefaultRouter()
router.register('laboratorios', LaboratorioViewSet, basename='laboratorio')

urlpatterns = router.urls
