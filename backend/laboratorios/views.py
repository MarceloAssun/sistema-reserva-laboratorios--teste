from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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

	@action(detail=True, methods=('get',), permission_classes=(permissions.IsAuthenticated,))
	def disponibilidade(self, request, pk=None):
		from reservas.models import Reserva
		from reservas.serializers import ReservaSerializer

		data = request.query_params.get('data')
		if not data:
			raise ValidationError({'data': 'Informe a data no formato AAAA-MM-DD.'})
		reservas = Reserva.objects.filter(
			laboratorio=self.get_object(), data=data, status=Reserva.Status.APROVADA,
		).order_by('hora_inicio')
		inicio = request.query_params.get('hora_inicio')
		fim = request.query_params.get('hora_fim')
		if bool(inicio) != bool(fim):
			raise ValidationError('Informe hora_inicio e hora_fim em conjunto.')
		if inicio and fim:
			if fim <= inicio:
				raise ValidationError({'hora_fim': 'A hora final deve ser posterior à inicial.'})
			reservas = reservas.filter(hora_inicio__lt=fim, hora_fim__gt=inicio)
		return Response({
			'laboratorio': self.get_object().pk, 'data': data,
			'disponivel': not reservas.exists(),
			'reservas': ReservaSerializer(reservas, many=True).data,
		})
