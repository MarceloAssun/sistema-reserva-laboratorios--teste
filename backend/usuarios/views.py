from django.contrib.auth.models import User
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.permissions import IsAdminGroup
from .serializers import PasswordResetSerializer, RegisterSerializer, UserSerializer, UserUpdateSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.prefetch_related('groups').order_by('username')
    permission_classes = (IsAdminGroup,)
    http_method_names = ('get', 'post', 'patch', 'head', 'options')

    def get_serializer_class(self):
        if self.action == 'redefinir_senha':
            return PasswordResetSerializer
        return UserUpdateSerializer if self.action in ('update', 'partial_update') else UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=('post',), url_path='redefinir-senha')
    def redefinir_senha(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            raise ValidationError('Superusuários devem ser gerenciados pelo Django Admin.')
        serializer = self.get_serializer(
            data=request.data,
            context={**self.get_serializer_context(), 'target_user': user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
