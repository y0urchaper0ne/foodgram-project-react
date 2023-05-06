from django.shortcuts import render

from rest_framework import filters, permissions, status, viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .serializers import UserSerializer, SignUpSerializer
from .permissions import IsAdminOrReadOnly

from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)

    @api_view(['GET', 'POST'])
    def users_list(request):
        if request.method == 'GET':
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            serializer = SignUpSerializer

