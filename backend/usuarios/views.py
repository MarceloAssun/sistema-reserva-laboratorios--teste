from django.contrib.auth.models import User
from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from reservas.permissions import IsAdminGroup
from .serializers import UserSerializer, UserUpdateSerializer


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
        response = super().update(request, *args, **kwargs)
        response.data = UserSerializer(self.get_object()).data
        return response
