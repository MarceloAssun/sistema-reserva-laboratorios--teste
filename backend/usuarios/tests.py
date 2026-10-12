from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class RegisterAPITests(APITestCase):
    url = '/api/auth/register/'

    def payload(self, **overrides):
        data = {
            'username': 'novo.aluno',
            'first_name': 'Novo',
            'last_name': 'Aluno',
            'email': 'novo.aluno@example.com',
            'password': 'SenhaSegura-TCC-2026',
            'password_confirm': 'SenhaSegura-TCC-2026',
        }
        data.update(overrides)
        return data

    def test_cadastro_publico_cria_somente_aluno(self):
        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='novo.aluno')
        self.assertTrue(user.check_password('SenhaSegura-TCC-2026'))
        self.assertEqual(list(user.groups.values_list('name', flat=True)), ['Alunos'])
        self.assertFalse(user.is_staff)
        self.assertNotIn('password', response.data)

    def test_rejeita_senhas_diferentes(self):
        response = self.client.post(
            self.url,
            self.payload(password_confirm='OutraSenha-TCC-2026'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_rejeita_usuario_e_email_duplicados_sem_diferenciar_maiusculas(self):
        User.objects.create_user(username='Novo.Aluno', email='NOVO.ALUNO@example.com')

        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
