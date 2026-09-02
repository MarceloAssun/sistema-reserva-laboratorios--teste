from django.contrib import admin

from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'professor', 'laboratorio', 'data', 'hora_inicio', 'hora_fim',
		'status', 'data_solicitacao',
	)
	list_filter = ('status', 'data', 'laboratorio')
	search_fields = ('professor__username', 'laboratorio__nome', 'observacao')
