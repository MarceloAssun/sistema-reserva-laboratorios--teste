from django.core.validators import MinValueValidator
from django.db import models

class Laboratorio(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    bloco = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
