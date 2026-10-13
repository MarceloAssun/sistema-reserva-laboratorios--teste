from django.utils import timezone
from rest_framework import serializers

from laboratorios.serializers import LaboratorioSerializer
from .models import Reserva
from .permissions import user_in_group
from .services import reservas_aprovadas_conflitantes


class AgendaReservaSerializer(serializers.ModelSerializer):
    laboratorio_nome = serializers.CharField(source='laboratorio.nome', read_only=True)
    laboratorio_bloco = serializers.CharField(source='laboratorio.bloco', read_only=True)

    class Meta:
        model = Reserva
        fields = (
            'id', 'laboratorio', 'laboratorio_nome', 'laboratorio_bloco',
            'data', 'hora_inicio', 'hora_fim',
        )


class ReservaSerializer(serializers.ModelSerializer):
    laboratorio_nome = serializers.CharField(source='laboratorio.nome', read_only=True)
    laboratorio_detalhes = LaboratorioSerializer(source='laboratorio', read_only=True)
    professor_nome = serializers.SerializerMethodField()
    professor_detalhes = serializers.SerializerMethodField()
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reserva
        fields = (
            'id', 'laboratorio', 'laboratorio_nome', 'laboratorio_detalhes',
            'professor', 'professor_nome', 'professor_detalhes',
            'data', 'hora_inicio', 'hora_fim', 'status', 'status_label',
            'observacao', 'data_solicitacao',
        )
        read_only_fields = ('professor', 'status', 'data_solicitacao')

    def get_professor_detalhes(self, obj):
        return {'id': obj.professor_id, 'nome': obj.professor.get_full_name() or obj.professor.username}

    def get_professor_nome(self, obj):
        return obj.professor.get_full_name() or obj.professor.username

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not user_in_group(request.user, 'Professores'):
            raise serializers.ValidationError('Somente professores podem solicitar reservas.')
        laboratorio = attrs.get('laboratorio')
        data = attrs.get('data')
        hora_inicio = attrs.get('hora_inicio')
        hora_fim = attrs.get('hora_fim')
        if not laboratorio.ativo:
            raise serializers.ValidationError({'laboratorio': 'O laboratório está inativo.'})
        if data < timezone.localdate():
            raise serializers.ValidationError({'data': 'A data deve ser hoje ou futura.'})
        if hora_fim <= hora_inicio:
            raise serializers.ValidationError({'hora_fim': 'A hora final deve ser posterior à inicial.'})
        instance = self.instance or Reserva(
            laboratorio=laboratorio, data=data, hora_inicio=hora_inicio, hora_fim=hora_fim,
        )
        instance.laboratorio = laboratorio
        instance.data = data
        instance.hora_inicio = hora_inicio
        instance.hora_fim = hora_fim
        return attrs

    def create(self, validated_data):
        return Reserva.objects.create(professor=self.context['request'].user, **validated_data)
