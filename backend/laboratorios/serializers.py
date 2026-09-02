from rest_framework import serializers

from .models import Laboratorio


class LaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ('id', 'nome', 'capacidade', 'bloco', 'ativo')
