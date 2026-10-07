from rest_framework.permissions import BasePermission


def user_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def is_admin(user):
    return user.is_superuser or user_in_group(user, 'Administradores')


class IsAdminGroup(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsProfessorGroup(BasePermission):
    def has_permission(self, request, view):
        return user_in_group(request.user, 'Professores')


class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return is_admin(request.user) or obj.professor_id == request.user.id
