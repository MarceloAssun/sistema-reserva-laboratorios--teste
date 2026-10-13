from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.dateparse import parse_date
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from laboratorios.models import Laboratorio
from .models import Reserva
from .permissions import IsAdminGroup, IsAdminOrOwner, IsProfessorGroup, is_admin
from .serializers import AgendaReservaSerializer, ReservaSerializer
from .services import aprovar_reserva, cancelar_reserva, rejeitar_reserva


class ReservaViewSet(viewsets.ModelViewSet):
	serializer_class = ReservaSerializer
	http_method_names = ('get', 'post', 'head', 'options')

	def get_queryset(self):
		queryset = Reserva.objects.select_related('laboratorio', 'professor').order_by('-data', '-hora_inicio')
		if not is_admin(self.request.user):
			queryset = queryset.filter(professor=self.request.user)
		params = self.request.query_params
		if params.get('status'):
			queryset = queryset.filter(status=params['status'])
		if params.get('laboratorio'):
			queryset = queryset.filter(laboratorio_id=params['laboratorio'])
		if params.get('professor') and is_admin(self.request.user):
			queryset = queryset.filter(professor_id=params['professor'])
		if params.get('data'):
			queryset = queryset.filter(data=params['data'])
		if params.get('data_inicio'):
			queryset = queryset.filter(data__gte=params['data_inicio'])
		if params.get('data_fim'):
			queryset = queryset.filter(data__lte=params['data_fim'])
		return queryset

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
			return Response({'detail': exc.messages[0]}, status=status.HTTP_409_CONFLICT)
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


class AgendaView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request):
		data_inicio = parse_date(request.query_params.get('data_inicio', ''))
		data_fim = parse_date(request.query_params.get('data_fim', ''))
		if not data_inicio or not data_fim:
			raise ValidationError({'detail': 'Informe data_inicio e data_fim no formato AAAA-MM-DD.'})
		if data_fim < data_inicio:
			raise ValidationError({'data_fim': 'A data final deve ser igual ou posterior à inicial.'})
		if (data_fim - data_inicio).days > 31:
			raise ValidationError({'data_fim': 'Consulte no máximo 32 dias por vez.'})

		reservas = Reserva.objects.select_related('laboratorio').filter(
			status=Reserva.Status.APROVADA,
			data__range=(data_inicio, data_fim),
		).order_by('data', 'hora_inicio', 'laboratorio__nome')
		laboratorio = request.query_params.get('laboratorio')
		if laboratorio:
			reservas = reservas.filter(laboratorio_id=laboratorio)
		return Response(AgendaReservaSerializer(reservas, many=True).data)
