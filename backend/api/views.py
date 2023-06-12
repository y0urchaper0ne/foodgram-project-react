from datetime import date

from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated, 
                                        IsAuthenticatedOrReadOnly, SAFE_METHODS)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (UserListSerializer, SignUpSerializer,
                          SubscriptionListSerializer, SubscribeSerializer,
                          TagListSerializer, IngredientsListSerializer,
                          RecipeListSerializer, PasswordSerializer,
                          RecipeCreateSerializer, FavouriteRecipeSerializer,)

from recipe.models import (Recipe, Ingredient, Tag, Favorite,
                           ShoppingСart, RecipeIngredients,)
from users.models import User, Subscribe


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserListSerializer
        return SignUpSerializer
    
    @action(detail=False, methods=['GET',],
            pagination_class=CustomPagination,
            permission_classes = (IsAuthenticated,))
    def me(self, request):
        serializer = UserListSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST',],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = PasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Ваш пароль был успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET',],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionListSerializer(page, many=True,
                                                context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE',],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = SubscribeSerializer(author, data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(author=author, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=request.user, author=author).delete()
            return Response({'detail': 'Вы отписались от пользователя'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagListSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientsListSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        IsAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        '''Получение объекта - автор рецепта'''
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            try:
                Favorite.objects.create(user=request.user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {'errors':
                     'Вы уже добавляли этот рецепт в список покупок!'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FavouriteRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Вы успешно удалили рецепт из избранного!'},
                status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Проверьте метод'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPagination)
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FavouriteRecipeSerializer(recipe, data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingСart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingСart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                {'errors': 'Вы уже добавляли этот рецепт в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingСart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Вы успешно удалили рецепт из списка покупок!'},
                status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Проверьте метод'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        current_date = date.today()
        if not user.shopping_cart.exists():
            return Response(
                {'detail': 'Ваш список покупок пуст!'},
                status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__shopping_cart_recipe__user=user)
            .values('ingredient')
            .annotate(total=Sum('amount'))
            .values_list('ingredient__name', 'total',
                         'ingredient__measurement_unit')
        )
        items_to_buy = (
            f'Дата: {current_date.strftime("%d/%m/%Y")}\n'
        )
        i = 1
        for ingredient in ingredients:
            items_to_buy += ''.join(
                '{}. {} - {} {}.\n'.format(i, *ingredient))
            i += 1

        filename = f'{user.username}_items_to_buy.txt'
        response = HttpResponse(items_to_buy, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response