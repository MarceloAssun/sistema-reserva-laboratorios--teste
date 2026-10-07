from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from laboratorios.models import Laboratorio
from reservas.models import Reserva


class Command(BaseCommand):
    help = 'Cria grupos, usuários e laboratórios para demonstração.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='Senha local dos usuários de demonstração.')

    def handle(self, *args, **options):
        password = options['password']
        groups = {
            name: Group.objects.get_or_create(name=name)[0]
            for name in ('Alunos', 'Professores', 'Administradores')
        }
        users = (
            ('aluno.demo', 'Alunos'),
            ('professor.demo', 'Professores'),
            ('admin.demo', 'Administradores'),
        )
        for username, group_name in users:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_staff = group_name == 'Administradores'
            user.save()
            user.groups.set((groups[group_name],))
            self.stdout.write(f'{"Criado" if created else "Atualizado"}: {username}')

        laboratories = (
            ('Laboratório de Informática 01', 30, 'A'),
            ('Laboratório de Informática 02', 25, 'A'),
            ('Laboratório de Eletrônica', 20, 'B'),
        )
        for nome, capacidade, bloco in laboratories:
            Laboratorio.objects.get_or_create(
                nome=nome,
                defaults={'capacidade': capacidade, 'bloco': bloco, 'ativo': True},
            )
        self.stdout.write(self.style.SUCCESS('Dados de demonstração prontos.'))
