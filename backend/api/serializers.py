import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import transaction

from djoser.serializers import UserSerializer, UserCreateSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipe.models import (Ingredient, Tag, Recipe,
                           Favorite, ShoppingCart,
                           RecipeIngredients,)
from users.models import Subscribe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserListSerializer(UserSerializer):
    """Вывод списка пользователей"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            if not request.user.is_anonymous:
                return Subscribe.objects.filter(
                    user=request.user,
                    author=obj).exists()
        return False


class SignUpSerializer(UserCreateSerializer):
    """Создание нового пользователя"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 
                  'first_name','last_name', 'password')

    def validate_username(self, value):
        value_lower = value.lower()
        username = User.objects.filter(username__iexact=value_lower)
        if username.exists():
            raise ValidationError('Пользователь с таким'
                                  ' username уже существует')
        return value_lower

    def validate_email(self, value):
        value_lower = value.lower()
        email = User.objects.filter(email__iexact=value_lower)
        if email.exists():
            raise ValidationError('Пользователь с таким'
                                  ' email уже существует')
        return value_lower


class PasswordSerializer(serializers.Serializer):
    """Изменение пароля"""
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                 {'new_password': list(error.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise ValidationError('Неверный пароль')
        if (validated_data['current_password']
            == validated_data['new_password']):
            raise ValidationError('Пароли совпадают')
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data
    

class FavouriteRecipeSerializer(serializers.ModelSerializer):
    """Вывод списка рецептов из избранного"""
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ['name', 'cooking_time',]


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Вывод подписчиков пользователя"""
    recipes_amount = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_amount',)

    def get_recipes_amount(self, obj):
        return obj.recipe.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            if not request.user.is_anonymous:
                return Subscribe.objects.filter(
                    user=request.user,
                    author=obj).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipe.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return FavouriteRecipeSerializer(recipes, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Подписка на пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = FavouriteRecipeSerializer(many=True,
                                        read_only=True)
    recipes_amount = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_amount',)
        read_only_fields = ['email', 'username',]

    def validate(self, obj):
        if (self.context.get('request').user == obj):
            raise ValidationError('Нельзя подписаться на себя')
        return obj

    def get_recipes_amount(self, obj):
        return obj.recipe.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            if not request.user.is_anonymous:
                return Subscribe.objects.filter(
                    user=request.user,
                    author=obj).exists()
        return False


class TagListSerializer(serializers.ModelSerializer):
    """Вывод списка тэгов"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsListSerializer(serializers.ModelSerializer):
    """Вывод списка ингридиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngrediensSerializer(serializers.ModelSerializer):
    """Список ингридиентов для рецепта"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'amount',
                  'measurement_unit',)


class RecipeListSerializer(serializers.ModelSerializer):
    """Вывод списка рецептов"""
    author = UserListSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagListSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngrediensSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=object).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=object).exists()


class IngredientsInReipe(serializers.ModelSerializer):
    """Добавление ингридиентов в рецепт"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount',)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингридиент')
        return value 


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание и изменение рецепта"""
    author = UserListSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsInReipe(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',)
        read_only_fields = ['id',]

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise serializers.ValidationError(
                    'Пожалуйста, заполните все поля!')
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Пожалуйста, укажите хотя бы один тег!')
        return obj
        
    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте как минимум один ингредиент')
    
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0')
        ing = [item['id'] for item in ingredients]
        if len(ing) != len(set(ing)):
            raise serializers.ValidationError(
                'Ингредиенты не могут повторяться'
            )
        return ingredients

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0')
        return value
    
    @transaction.atomic
    def add_tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredients.objects.bulk_create(
            [RecipeIngredients(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('author')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.add_tags_and_ingredients(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredients.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.add_tags_and_ingredients(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance,
                                    context=self.context).data
