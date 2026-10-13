from django.contrib.auth.models import Group, User
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

    def test_cadastro_ignora_tentativa_de_escolher_perfil_privilegiado(self):
        response = self.client.post(
            self.url,
            self.payload(perfil='ADMINISTRADOR', is_staff=True, is_superuser=True),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='novo.aluno')
        self.assertEqual(list(user.groups.values_list('name', flat=True)), ['Alunos'])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class ProfilePermissionTests(APITestCase):
    def setUp(self):
        self.groups = {
            name: Group.objects.create(name=name)
            for name in ('Alunos', 'Professores', 'Administradores')
        }
        self.aluno = self.create_user('aluno', 'Alunos')
        self.professor = self.create_user('professor', 'Professores')
        self.admin = self.create_user('admin', 'Administradores')

    def create_user(self, username, group):
        user = User.objects.create_user(username=username, password='SenhaSegura-TCC-2026')
        user.groups.add(self.groups[group])
        return user

    def test_usuario_atual_informa_perfil_correto(self):
        for user, perfil in (
            (self.aluno, 'ALUNO'),
            (self.professor, 'PROFESSOR'),
            (self.admin, 'ADMINISTRADOR'),
        ):
            with self.subTest(perfil=perfil):
                self.client.force_authenticate(user)
                response = self.client.get('/api/auth/me/')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['perfil'], perfil)

    def test_aluno_e_professor_nao_gerenciam_usuarios(self):
        for user in (self.aluno, self.professor):
            with self.subTest(usuario=user.username):
                self.client.force_authenticate(user)
                self.assertEqual(
                    self.client.get('/api/usuarios/').status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.patch(
                        f'/api/usuarios/{self.aluno.pk}/',
                        {'perfil': 'PROFESSOR'},
                        format='json',
                    ).status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_administrador_promove_aluno_para_professor(self):
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            f'/api/usuarios/{self.aluno.pk}/',
            {'perfil': 'PROFESSOR'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['perfil'], 'PROFESSOR')
        self.assertEqual(
            list(self.aluno.groups.values_list('name', flat=True)),
            ['Professores'],
        )

    def test_administrador_nao_altera_o_proprio_perfil(self):
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            f'/api/usuarios/{self.admin.pk}/',
            {'perfil': 'ALUNO'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.admin.groups.filter(name='Administradores').exists())
