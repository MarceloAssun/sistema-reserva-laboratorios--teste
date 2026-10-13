from django.contrib.auth.models import User
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.permissions import IsAdminGroup
from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer


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
    http_method_names = ('get', 'patch', 'head', 'options')

    def get_serializer_class(self):
        return UserUpdateSerializer if self.action in ('update', 'partial_update') else UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)
