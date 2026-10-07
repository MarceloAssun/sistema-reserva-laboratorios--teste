from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from laboratorios.models import Laboratorio
# Create your models here.

class Reserva(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADA = 'APROVADA', 'Aprovada'
        REJEITADA = 'REJEITADA', 'Rejeitada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.PROTECT
        , related_name='reservas'
    )

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
        , related_name='reservas'
    )

    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    observacao = models.TextField(blank=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.hora_fim <= self.hora_inicio:
            raise ValidationError({'hora_fim': 'A hora final deve ser posterior à hora inicial.'})
        if not self.laboratorio.ativo:
            raise ValidationError({'laboratorio': 'O laboratório está inativo.'})

    class Meta:
        ordering = ('-data', '-hora_inicio')
        constraints = (
            models.CheckConstraint(
                condition=models.Q(hora_fim__gt=models.F('hora_inicio')),
                name='reserva_hora_fim_apos_inicio',
            ),
        )

    def __str__(self):
        return f"Reserva {self.id} - {self.laboratorio.nome} - {self.data} {self.hora_inicio}-{self.hora_fim}"
