from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from laboratorios.models import Laboratorio
from .models import Reserva
from .permissions import IsAdminGroup, IsAdminOrOwner, IsProfessorGroup, is_admin
from .serializers import ReservaSerializer
from .services import aprovar_reserva, cancelar_reserva, rejeitar_reserva


class ReservaViewSet(viewsets.ModelViewSet):
	serializer_class = ReservaSerializer
	http_method_names = ('get', 'post', 'patch', 'head', 'options')

	def get_queryset(self):
		queryset = Reserva.objects.select_related('laboratorio', 'professor').order_by('-data', '-hora_inicio')
		if is_admin(self.request.user):
			return queryset
		return queryset.filter(professor=self.request.user)

	def get_permissions(self):
		if self.action == 'create':
			return [IsProfessorGroup()]
		if self.action in ('aprovar', 'rejeitar'):
			return [IsAdminGroup()]
		if self.action == 'cancelar':
			return [permissions.IsAuthenticated(), IsAdminOrOwner()]
		return [permissions.IsAuthenticated()]

	@action(detail=True, methods=('post',))
	def aprovar(self, request, pk=None):
		try:
			reserva = aprovar_reserva(self.get_object())
		except DjangoValidationError as exc:
			raise ValidationError(exc.messages)
		return Response(self.get_serializer(reserva).data)

	@action(detail=True, methods=('post',))
	def rejeitar(self, request, pk=None):
		try:
			reserva = rejeitar_reserva(self.get_object())
		except DjangoValidationError as exc:
			raise ValidationError(exc.messages)
		return Response(self.get_serializer(reserva).data)

	@action(detail=True, methods=('post',))
	def cancelar(self, request, pk=None):
		try:
			reserva = cancelar_reserva(self.get_object())
		except DjangoValidationError as exc:
			raise ValidationError(exc.messages)
		return Response(self.get_serializer(reserva).data)


class DisponibilidadeView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request):
		laboratorio_id = request.query_params.get('laboratorio')
		data = request.query_params.get('data')
		if not laboratorio_id or not data:
			raise ValidationError({'detail': 'Informe laboratorio e data.'})
		try:
			laboratorio = Laboratorio.objects.get(pk=laboratorio_id)
		except Laboratorio.DoesNotExist:
			raise ValidationError({'laboratorio': 'Laboratório não encontrado.'})
		reservas = Reserva.objects.filter(
			laboratorio=laboratorio,
			data=data,
			status=Reserva.Status.APROVADA,
		).order_by('hora_inicio')
		return Response({
			'laboratorio': laboratorio.id,
			'data': data,
			'reservas': ReservaSerializer(reservas, many=True).data,
		})
