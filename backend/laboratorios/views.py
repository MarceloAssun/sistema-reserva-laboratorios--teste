from rest_framework import permissions, viewsets

from reservas.permissions import IsAdminGroup
from .models import Laboratorio
from .serializers import LaboratorioSerializer


class LaboratorioViewSet(viewsets.ModelViewSet):
	queryset = Laboratorio.objects.all().order_by('bloco', 'nome')
	serializer_class = LaboratorioSerializer

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [IsAdminGroup()]
