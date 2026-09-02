from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase

from laboratorios.models import Laboratorio
from .models import Reserva
from .services import aprovar_reserva


class ReservaBusinessRulesTests(TestCase):
	def setUp(self):
		self.professor = User.objects.create_user('professor', password='test-pass')
		Group.objects.create(name='Professores').user_set.add(self.professor)
		User.objects.create_user('admin', password='test-pass', is_staff=True)
		self.laboratorio = Laboratorio.objects.create(
			nome='Laboratório de Teste', capacidade=20, bloco='A'
		)
		self.data = date.today() + timedelta(days=1)

	def make_reserva(self, inicio, fim):
		return Reserva.objects.create(
			laboratorio=self.laboratorio,
			professor=self.professor,
			data=self.data,
			hora_inicio=time(*inicio),
			hora_fim=time(*fim),
		)

	def test_aprovacao_bloqueia_horario_conflitante(self):
		primeira = self.make_reserva((8, 0), (10, 0))
		primeira.status = Reserva.Status.APROVADA
		primeira.save(update_fields=('status',))
		segunda = self.make_reserva((9, 0), (11, 0))

		with self.assertRaisesMessage(ValidationError, 'conflitante'):
			aprovar_reserva(segunda)

	def test_aprovacao_permite_horarios_adjacentes(self):
		primeira = self.make_reserva((8, 0), (10, 0))
		primeira.status = Reserva.Status.APROVADA
		primeira.save(update_fields=('status',))
		segunda = self.make_reserva((10, 0), (11, 0))

		aprovar_reserva(segunda)

		segunda.refresh_from_db()
		self.assertEqual(segunda.status, Reserva.Status.APROVADA)
