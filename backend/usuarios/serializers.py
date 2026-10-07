from django.contrib.auth.models import Group, User
from rest_framework import serializers


PERFIS = {
    'ALUNO': 'Alunos',
    'PROFESSOR': 'Professores',
    'ADMINISTRADOR': 'Administradores',
}


class UserSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    grupos = serializers.SlugRelatedField(source='groups', many=True, read_only=True, slug_field='name')
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    perfil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'nome', 'name', 'groups', 'grupos', 'perfil', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser')
        read_only_fields = fields

    def get_nome(self, obj):
        return obj.get_full_name() or obj.username

    def get_name(self, obj):
        return self.get_nome(obj)

    def get_perfil(self, obj):
        names = set(obj.groups.values_list('name', flat=True))
        if obj.is_superuser or 'Administradores' in names:
            return 'ADMINISTRADOR'
        if 'Professores' in names:
            return 'PROFESSOR'
        return 'ALUNO'


class UserUpdateSerializer(serializers.ModelSerializer):
    perfil = serializers.ChoiceField(choices=tuple(PERFIS))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active', 'perfil')

    def validate(self, attrs):
        if self.instance.is_superuser:
            raise serializers.ValidationError('Superusuários devem ser gerenciados pelo Django Admin.')
        if self.instance == self.context['request'].user:
            raise serializers.ValidationError('Você não pode alterar seu próprio perfil administrativo.')
        return attrs

    def update(self, instance, validated_data):
        perfil = validated_data.pop('perfil')
        instance = super().update(instance, validated_data)
        grupos_perfil = Group.objects.filter(name__in=PERFIS.values())
        instance.groups.remove(*grupos_perfil)
        instance.groups.add(Group.objects.get_or_create(name=PERFIS[perfil])[0])
        return instance
