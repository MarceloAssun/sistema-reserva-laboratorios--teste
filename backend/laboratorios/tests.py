from django.contrib.auth.models import Group, User
from rest_framework.test import APITestCase

from .models import Laboratorio


class LaboratorioAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin')
        self.admin.groups.add(Group.objects.create(name='Administradores'))
        self.usuario = User.objects.create_user('usuario')

    def test_administrador_cria_laboratorio(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/laboratorios/', {'nome': 'Lab', 'capacidade': 30, 'bloco': 'A'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Laboratorio.objects.filter(nome='Lab').exists())

    def test_usuario_comum_apenas_consulta(self):
        self.client.force_authenticate(self.usuario)
        self.assertEqual(self.client.get('/api/laboratorios/').status_code, 200)
        self.assertEqual(self.client.post('/api/laboratorios/', {}).status_code, 403)

    def test_health_check_e_publico_e_confirma_banco(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'ok', 'database': 'ok'})
