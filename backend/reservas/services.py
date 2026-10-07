from django.core.exceptions import ValidationError
from django.db import transaction

from laboratorios.models import Laboratorio

from .models import Reserva


def reservas_aprovadas_conflitantes(reserva):
    return Reserva.objects.filter(
        laboratorio=reserva.laboratorio,
        data=reserva.data,
        status=Reserva.Status.APROVADA,
        hora_inicio__lt=reserva.hora_fim,
        hora_fim__gt=reserva.hora_inicio,
    ).exclude(pk=reserva.pk)


@transaction.atomic
def aprovar_reserva(reserva):
    reserva = Reserva.objects.select_for_update().select_related('laboratorio').get(pk=reserva.pk)
    # Uma única linha do laboratório serializa aprovações concorrentes do mesmo espaço.
    Laboratorio.objects.select_for_update().get(pk=reserva.laboratorio_id)
    if reserva.status != Reserva.Status.PENDENTE:
        raise ValidationError('Somente solicitações pendentes podem ser aprovadas.')
    if not reserva.laboratorio.ativo:
        raise ValidationError('O laboratório está inativo.')
    if reservas_aprovadas_conflitantes(reserva).exists():
        raise ValidationError('Já existe uma reserva aprovada conflitante para este laboratório e horário.')
    reserva.status = Reserva.Status.APROVADA
    reserva.save(update_fields=('status',))
    return reserva


@transaction.atomic
def rejeitar_reserva(reserva):
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.status != Reserva.Status.PENDENTE:
        raise ValidationError('Somente solicitações pendentes podem ser rejeitadas.')
    reserva.status = Reserva.Status.REJEITADA
    reserva.save(update_fields=('status',))
    return reserva


@transaction.atomic
def cancelar_reserva(reserva):
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.status == Reserva.Status.CANCELADA:
        raise ValidationError('A reserva já está cancelada.')
    if reserva.status == Reserva.Status.REJEITADA:
        raise ValidationError('Uma reserva rejeitada não pode ser cancelada.')
    reserva.status = Reserva.Status.CANCELADA
    reserva.save(update_fields=('status',))
    return reserva
