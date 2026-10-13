from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from laboratorios.models import Laboratorio
from .models import Reserva
from .services import aprovar_reserva


class ReservaAPITests(TestCase):
    def setUp(self):
        self.aluno = User.objects.create_user('aluno')
        self.professor = User.objects.create_user('professor')
        self.outro = User.objects.create_user('outro')
        self.admin = User.objects.create_user('admin')
        for user, grupo in ((self.aluno, 'Alunos'), (self.professor, 'Professores'), (self.outro, 'Professores'), (self.admin, 'Administradores')):
            user.groups.add(Group.objects.get_or_create(name=grupo)[0])
        self.lab = Laboratorio.objects.create(nome='Laboratório 01', capacidade=20, bloco='A')
        self.data = date.today() + timedelta(days=2)
        self.client = APIClient()

    def payload(self, inicio='08:00', fim='10:00', laboratorio=None):
        return {'laboratorio': laboratorio or self.lab.pk, 'data': self.data, 'hora_inicio': inicio, 'hora_fim': fim, 'observacao': 'Aula'}

    def criar(self, user=None, **changes):
        self.client.force_authenticate(user or self.professor)
        payload = self.payload()
        payload.update(changes)
        return self.client.post('/api/reservas/', payload, format='json')

    def reserva(self, professor=None, inicio='08:00', fim='10:00', status='PENDENTE'):
        return Reserva.objects.create(
            laboratorio=self.lab, professor=professor or self.professor,
            data=self.data, hora_inicio=inicio, hora_fim=fim,
            observacao='Aula', status=status,
        )

    def test_professor_cria_pendente_sem_forjar_autoria(self):
        response = self.criar(professor=self.outro.pk, status='APROVADA')
        self.assertEqual(response.status_code, 201)
        reserva = Reserva.objects.get()
        self.assertEqual((reserva.professor, reserva.status), (self.professor, 'PENDENTE'))

    def test_aluno_nao_cria_e_inativo_nao_aceita(self):
        self.assertEqual(self.criar(self.aluno).status_code, 403)
        self.lab.ativo = False
        self.lab.save()
        self.assertEqual(self.criar().status_code, 400)

    def test_administrador_nao_cria_reserva_em_nome_de_professor(self):
        self.assertEqual(self.criar(self.admin).status_code, 403)

    def test_visibilidade_por_perfil(self):
        self.reserva()
        self.reserva(self.outro, '10:00', '12:00')
        self.client.force_authenticate(self.professor)
        self.assertEqual(len(self.client.get('/api/reservas/').data), 1)
        self.client.force_authenticate(self.admin)
        self.assertEqual(len(self.client.get('/api/reservas/').data), 2)

    def test_acoes_e_permissoes(self):
        reserva = self.reserva()
        self.client.force_authenticate(self.professor)
        self.assertEqual(self.client.post(f'/api/reservas/{reserva.pk}/aprovar/').status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post(f'/api/reservas/{reserva.pk}/aprovar/').status_code, 200)
        outra = self.reserva(inicio='10:00', fim='12:00')
        self.assertEqual(self.client.post(f'/api/reservas/{outra.pk}/rejeitar/').status_code, 200)
        terceira = self.reserva(inicio='12:00', fim='13:00')
        self.client.force_authenticate(self.professor)
        self.assertEqual(self.client.post(f'/api/reservas/{terceira.pk}/cancelar/').status_code, 200)
        terceira.refresh_from_db()
        self.assertEqual(terceira.status, 'CANCELADA')

    def test_administrador_cancela_reserva_aprovada(self):
        reserva = self.reserva(status='APROVADA')
        self.client.force_authenticate(self.admin)

        response = self.client.post(f'/api/reservas/{reserva.pk}/cancelar/')

        self.assertEqual(response.status_code, 200)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'CANCELADA')

    def test_professor_nao_acessa_nem_cancela_reserva_de_outro_professor(self):
        reserva = self.reserva(professor=self.outro)
        self.client.force_authenticate(self.professor)

        self.assertEqual(
            self.client.get(f'/api/reservas/{reserva.pk}/').status_code,
            404,
        )
        self.assertEqual(
            self.client.post(f'/api/reservas/{reserva.pk}/cancelar/').status_code,
            404,
        )
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'PENDENTE')

    def test_reserva_nao_aceita_patch_generico(self):
        reserva = self.reserva()
        self.client.force_authenticate(self.professor)

        response = self.client.patch(
            f'/api/reservas/{reserva.pk}/',
            {'status': 'APROVADA', 'observacao': 'Alterada'},
            format='json',
        )

        self.assertEqual(response.status_code, 405)
        reserva.refresh_from_db()
        self.assertEqual((reserva.status, reserva.observacao), ('PENDENTE', 'Aula'))

    def test_disponibilidade_so_mostra_aprovadas(self):
        aprovada = self.reserva(status='APROVADA')
        self.reserva(inicio='10:00', fim='11:00', status='REJEITADA')
        self.client.force_authenticate(self.aluno)
        response = self.client.get(f'/api/laboratorios/{self.lab.pk}/disponibilidade/?data={self.data}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['reservas']], [aprovada.pk])


class ConflitoTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user('professor')
        self.lab = Laboratorio.objects.create(nome='Lab', capacidade=10, bloco='B')
        self.data = date.today() + timedelta(days=1)
        self.base = Reserva.objects.create(laboratorio=self.lab, professor=self.professor, data=self.data, hora_inicio=time(8), hora_fim=time(10), status='APROVADA')

    def nova(self, inicio, fim):
        return Reserva.objects.create(laboratorio=self.lab, professor=self.professor, data=self.data, hora_inicio=time(*inicio), hora_fim=time(*fim))

    def test_conflitos_e_adjacencias(self):
        for inicio, fim in [((7, 0), (9, 0)), ((8, 0), (9, 0)), ((9, 0), (11, 0)), ((7, 0), (11, 0)), ((8, 0), (10, 0))]:
            with self.subTest(inicio=inicio, fim=fim), self.assertRaises(ValidationError):
                aprovar_reserva(self.nova(inicio, fim))
        for inicio, fim in [((6, 0), (8, 0)), ((10, 0), (12, 0))]:
            reserva = self.nova(inicio, fim)
            aprovar_reserva(reserva)
            reserva.delete()

    def test_rejeitada_e_cancelada_nao_bloqueiam(self):
        for estado in ('REJEITADA', 'CANCELADA'):
            self.base.status = estado
            self.base.save()
            nova = self.nova((8, 0), (10, 0))
            aprovar_reserva(nova)
            nova.delete()
