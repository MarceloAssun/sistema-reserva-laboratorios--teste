from rest_framework import serializers

from .models import Laboratorio


class LaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ('id', 'nome', 'capacidade', 'bloco', 'ativo')

    def validate_nome(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Informe o nome do laboratório.')
        return value

    def validate_bloco(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Informe o bloco.')
        return value
