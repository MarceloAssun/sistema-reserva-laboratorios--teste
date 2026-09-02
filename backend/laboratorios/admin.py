from django.contrib import admin
from .models import Laboratorio

# Register your models here.

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome', 
        'capacidade', 
        'bloco', 
        'ativo'
        )
    
    list_filter = (
        'ativo', 
        'bloco'
        )

    search_fields = (
        'nome',
        'bloco'
        )